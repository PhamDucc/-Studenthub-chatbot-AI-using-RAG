"""Lightweight lexical retrieval and source excerpts for offline demo use."""

from collections import Counter
from functools import lru_cache
import math
import re
import unicodedata

from ..config import TOP_K
from ..repositories.documents import data_signature, load_passages
from ..models import Hit, Passage


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    return "".join("d" if c == "đ" else c for c in value if unicodedata.category(c) != "Mn")


STOP_WORDS = {normalize(word) for word in {
    "và", "là", "của", "cho", "có", "được", "với", "trong", "khi",
    "ở", "tại", "về", "theo", "nào", "bao", "nhiêu", "như", "thế", "để",
    "em", "mình", "tôi", "bạn", "anh", "chị", "sinh", "viên", "trường",
    "cần", "phải", "đã", "sẽ", "một", "các", "những", "nếu", "không",
}}


def tokens(value: str) -> list[str]:
    value = normalize(value)
    return [w for w in re.findall(r"[a-z0-9]+", value) if len(w) > 1 and w not in STOP_WORDS]


@lru_cache(maxsize=2)
def _index(signature: tuple[tuple[str, int, int], ...]) -> tuple[list[Passage], list[Counter[str]], Counter[str], float]:
    passages = load_passages()
    counts = [Counter(tokens(p.heading + " " + p.text)) for p in passages]
    document_frequency: Counter[str] = Counter()
    for count in counts:
        document_frequency.update(count.keys())
    avg_length = sum(sum(c.values()) for c in counts) / max(len(counts), 1)
    return passages, counts, document_frequency, avg_length


def search(question: str, limit: int = TOP_K) -> list[Hit]:
    passages, counts, df, avg_length = _index(data_signature())
    query_tokens = tokens(question)
    terms = set(query_tokens)
    if not terms:
        return []
    query_heading_phrases = {
        size: {tuple(query_tokens[i:i + size]) for i in range(len(query_tokens) - size + 1)}
        for size in (2, 3)
    }
    n = len(passages)
    term_idf = {
        term: math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
        for term in terms
    }
    results: list[Hit] = []
    for passage, count in zip(passages, counts):
        length = sum(count.values())
        score = 0.0
        for term in terms:
            frequency = count[term]
            if not frequency:
                continue
            score += term_idf[term] * frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / max(avg_length, 1)))
        heading_terms = set(tokens(passage.heading))
        score += sum(0.7 for term in terms & heading_terms)
        heading_tokens = tokens(passage.heading)
        for size, weight in ((2, 1.8), (3, 2.5)):
            passage_heading_phrases = {tuple(heading_tokens[i:i + size]) for i in range(len(heading_tokens) - size + 1)}
            score += weight * len(passage_heading_phrases & query_heading_phrases[size])
        if score > 0:
            results.append(Hit(passage, score))
    results.sort(key=lambda hit: hit.score, reverse=True)
    return results[:limit] if results and results[0].score >= 1.5 else []


def extract_answer(question: str, hits: list[Hit]) -> str:
    """Return cited source lines when Gemini is not configured or available."""
    query_terms = set(tokens(question))
    query_tokens = tokens(question)
    phrases = {tuple(query_tokens[index:index + 2]) for index in range(len(query_tokens) - 1)}
    passages, _, df, _ = _index(data_signature())
    n = len(passages)
    term_idf = {
        term: math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
        for term in query_terms
    }
    ranked_lines: list[tuple[float, int, str]] = []
    seen: set[str] = set()
    for source_number, hit in enumerate(hits, 1):
        for line in hit.passage.text.splitlines():
            line = line.strip()
            if len(line) < 20 or line == "---" or line in seen:
                continue
            seen.add(line)
            line_tokens = tokens(line)
            overlap = query_terms & set(line_tokens)
            if overlap:
                line_phrases = {tuple(line_tokens[index:index + 2]) for index in range(len(line_tokens) - 1)}
                score = sum(term_idf[term] for term in overlap) / max(len(line_tokens), 1) ** 0.25
                score += 2.0 * len(phrases & line_phrases) + 0.2 / source_number
                ranked_lines.append((score, source_number, line))
    ranked_lines.sort(reverse=True)
    excerpts = []
    for _, number, line in ranked_lines[:5]:
        clean_line = re.sub(r"^[-*]\s+", "", line)
        excerpts.append(f"- {clean_line[:500]} [{number}]")
    if not excerpts:
        excerpts = [hits[0].passage.text[:900] + " [1]"]
    return "Các dòng liên quan trong tài liệu:\n\n" + "\n".join(excerpts)
