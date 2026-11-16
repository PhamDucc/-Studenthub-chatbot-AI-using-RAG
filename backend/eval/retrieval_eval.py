"""Retrieval metrics: hit@k and MRR by expected source file."""

from collections.abc import Callable
from dataclasses import dataclass

from ..models import Hit
from .cases import Case


@dataclass
class Row:
    case: Case
    rank: int | None  # 1-based rank of the first hit that answers the case
    sources: list[str]


def is_relevant(case: Case, hit: Hit) -> bool:
    """Passage-level when anchors are known (heading match), otherwise file-level."""
    if hit.passage.source not in case.sources:
        return False
    if not case.anchors:
        return True
    heading = hit.passage.heading.lower()
    return any(anchor.lower() in heading for anchor in case.anchors)


def evaluate(cases: list[Case], search: Callable[[str], list[Hit]]) -> list[Row]:
    rows = []
    for case in cases:
        if case.unanswerable:
            continue
        hits = search(case.question)
        rank = next((i for i, hit in enumerate(hits, 1) if is_relevant(case, hit)), None)
        rows.append(Row(case, rank, [hit.passage.source for hit in hits]))
    return rows


def summarize(rows: list[Row]) -> dict:
    n = max(len(rows), 1)
    return {
        "cases": len(rows),
        "hit@1": sum(1 for r in rows if r.rank == 1) / n,
        "hit@3": sum(1 for r in rows if r.rank and r.rank <= 3) / n,
        "hit@6": sum(1 for r in rows if r.rank) / n,
        "mrr": sum(1 / r.rank for r in rows if r.rank) / n,
    }
