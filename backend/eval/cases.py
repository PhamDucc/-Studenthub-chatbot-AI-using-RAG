"""Load evaluation cases: the supplied 20-case benchmark plus paraphrase cases."""

from dataclasses import dataclass, field
import json
from pathlib import Path
import re

BENCHMARK = Path(__file__).resolve().parents[2] / "chatbot" / "tests" / "Smoke_Test_for_RAG.md"
PARAPHRASES = Path(__file__).with_name("paraphrases.json")


@dataclass(frozen=True)
class Case:
    id: str
    question: str
    sources: tuple[str, ...]
    keywords: tuple[str, ...] = field(default_factory=tuple)
    group: str = "benchmark"
    anchors: tuple[str, ...] = ()  # heading substrings that mark the answer-bearing passage
    unanswerable: bool = False  # the knowledge base has no answer; the bot should abstain
    offtopic: bool = False  # clearly unrelated to the university; retrieval should return nothing


def load_benchmark(path: Path = BENCHMARK) -> list[Case]:
    cases = []
    for section in re.split(r"(?=^### TC-\d+:)", path.read_text(encoding="utf-8"), flags=re.M)[1:]:
        question = re.search(r'\* \*\*Câu hỏi kiểm thử:\*\* \*"(.+?)"\*', section).group(1)
        source_line = re.search(r"\* \*\*Tệp dữ liệu nguồn:\*\* (.+)", section).group(1)
        keyword_line = re.search(r"\* \*\*Từ khóa bắt buộc:\*\* (.+)", section)
        cases.append(Case(
            id=re.search(r"TC-\d+", section).group(),
            question=question,
            sources=tuple(re.findall(r"`([^`]+\.md)`", source_line)),
            keywords=tuple(re.findall(r"`([^`]+)`", keyword_line.group(1))) if keyword_line else (),
        ))
    return cases


def load_paraphrases(path: Path = PARAPHRASES) -> list[Case]:
    if not path.is_file():
        return []
    return [Case(item["id"], item["question"], tuple(item["sources"]), tuple(item.get("keywords", ())), "paraphrase",
                 tuple(item.get("anchors", ())), item.get("unanswerable", False), item.get("offtopic", False))
            for item in json.loads(path.read_text(encoding="utf-8"))]


def load_all() -> list[Case]:
    return load_benchmark() + load_paraphrases()
