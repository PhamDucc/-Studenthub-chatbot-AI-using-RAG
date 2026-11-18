"""Values passed between loading, retrieval, chat, and HTTP layers."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class ConversationTurn:
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class Passage:
    source: str
    title: str
    heading: str
    text: str


@dataclass(frozen=True)
class Hit:
    passage: Passage
    score: float


@dataclass(frozen=True)
class ChatResult:
    answer: str
    hits: list[Hit]
    warning: str | None = None
    mode: Literal["gemini", "extractive", "no_match"] = "extractive"
    follow_ups: list[str] = field(default_factory=list)
