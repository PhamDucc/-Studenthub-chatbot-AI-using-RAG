"""Read the existing Markdown knowledge base into search passages."""

from pathlib import Path
import re

from ..config import DATA_DIR
from ..models import Passage


def data_signature(data_dir: Path = DATA_DIR) -> tuple[tuple[str, int, int], ...]:
    """Change when a Markdown file is added, edited, or removed."""
    return tuple(
        (path.name, path.stat().st_mtime_ns, path.stat().st_size)
        for path in sorted(data_dir.glob("*.md"))
    )


def _front_matter(text: str) -> tuple[str, str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", text, re.S)
    if not match:
        return "", text
    title = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', match.group(1), re.M)
    return (title.group(1).strip('"\'') if title else ""), match.group(2)


def _split_long(text: str, max_chars: int = 1800) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    blocks = re.split(r"\n\s*\n", text)
    result: list[str] = []
    current = ""
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if current and len(current) + len(block) + 2 > max_chars:
            result.append(current)
            current = ""
        if len(block) > max_chars:
            remaining = block
            while remaining:
                if len(remaining) <= max_chars:
                    piece, remaining = remaining, ""
                else:
                    boundary = remaining.rfind("\n", 0, max_chars)
                    if boundary < max_chars // 2:
                        boundary = remaining.rfind(" ", 0, max_chars)
                    if boundary < max_chars // 2:
                        boundary = max_chars
                    piece, remaining = remaining[:boundary].strip(), remaining[boundary:].strip()
                if current:
                    result.append(current)
                    current = ""
                result.append(piece)
        else:
            current = f"{current}\n\n{block}".strip()
    if current:
        result.append(current)
    return result


def load_passages(data_dir: Path = DATA_DIR) -> list[Passage]:
    passages: list[Passage] = []
    for path in sorted(data_dir.glob("*.md")):
        title, body = _front_matter(path.read_text(encoding="utf-8"))
        heading = title or path.stem.replace("_", " ")
        headings: dict[int, str] = {}
        section: list[str] = []

        def flush() -> None:
            text = "\n".join(section).strip()
            if text:
                for piece in _split_long(text):
                    passages.append(Passage(path.name, title or path.stem, heading, piece))
            section.clear()

        for line in body.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                flush()
                level = len(match.group(1))
                headings = {key: value for key, value in headings.items() if key < level}
                headings[level] = match.group(2).strip("* ")
                heading = " > ".join(headings[key] for key in sorted(headings) if key > 1) or headings[level]
            else:
                section.append(line)
        flush()
    return passages
