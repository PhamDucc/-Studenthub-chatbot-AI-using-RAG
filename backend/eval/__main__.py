"""python -m backend.eval [--group benchmark|paraphrase] [--verbose]"""

import argparse
import os

from ..services.retrieval import search
from .cases import load_all
from .retrieval_eval import evaluate, summarize


def run_followups() -> None:
    import json
    from pathlib import Path

    from ..models import ConversationTurn
    from ..services.rewrite import concatenated, rewrite_query
    from .cases import Case
    from .retrieval_eval import is_relevant

    raw = json.loads(Path(__file__).with_name("followups.json").read_text(encoding="utf-8"))
    strategies = {
        "raw (no context)": lambda q, h: q,
        "concatenate": concatenated,
        "rewrite": rewrite_query,
    }
    for name, build in strategies.items():
        ranks = []
        for item in raw:
            case = Case(item["id"], item["question"], tuple(item["sources"]), anchors=tuple(item["anchors"]))
            history = [ConversationTurn("user", item["history"])]
            query = build(item["question"], history)
            hits = search(query)
            ranks.append(next((i for i, h in enumerate(hits, 1) if is_relevant(case, h)), None))
        n = len(ranks)
        print(f"{name:<17} hit@1={sum(r == 1 for r in ranks) / n:.2f} hit@3={sum(bool(r and r <= 3) for r in ranks) / n:.2f} "
              f"mrr={sum(1 / r for r in ranks if r) / n:.3f}  ranks={ranks}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval quality.")
    parser.add_argument("--group", choices=["benchmark", "paraphrase"])
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--rerank", action="store_true", help="LLM-rerank candidates (uses Gemini quota)")
    parser.add_argument("--followups", action="store_true", help="evaluate query rewriting on follow-up questions")
    parser.add_argument("--no-dense", action="store_true", help="BM25 only (offline, deterministic)")
    args = parser.parse_args()
    if args.rerank:
        os.environ["RAG_RERANK"] = "1"
        os.environ.setdefault("RERANK_RETRIES", "3")
    if args.no_dense:
        os.environ["RAG_DENSE"] = "0"
    if not args.no_dense:
        os.environ.setdefault("EMBED_QUERY_RETRIES", "4")  # the eval fires many queries; ride out 429s
        from ..repositories.documents import load_passages
        from ..services.embeddings import ensure_index
        print("dense index ready:", ensure_index(load_passages()))
    if args.followups:
        run_followups()
        return
    cases = [c for c in load_all() if not args.group or c.group == args.group]
    rows = evaluate(cases, search)
    for group in sorted({r.case.group for r in rows}):
        part = [r for r in rows if r.case.group == group]
        s = summarize(part)
        print(f"{group:<11} n={s['cases']:<3} hit@1={s['hit@1']:.2f} hit@3={s['hit@3']:.2f} hit@6={s['hit@6']:.2f} mrr={s['mrr']:.3f}")
    offtopic = [c for c in cases if c.offtopic]
    if offtopic:
        leaked = [c for c in offtopic if search(c.question)]
        print(f"off-topic abstain: {len(offtopic) - len(leaked)}/{len(offtopic)}" + "".join(f"\n  leaked {c.id}: {c.question}" for c in leaked))
    for r in rows:
        if args.verbose or r.rank is None or r.rank > 1:
            print(f"  {r.case.id:<8} rank={r.rank}  want={','.join(s[:18] for s in r.case.sources)}  got={[s[:14] for s in r.sources[:3]]}  | {r.case.question[:60]}")


if __name__ == "__main__":
    main()
