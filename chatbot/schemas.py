"""
BƯỚC 1 - SCHEMAS
Khai báo cấu trúc dữ liệu mà pipeline RAG đọc/ghi. Sai cấu trúc -> báo lỗi ngay lúc đọc file,
không để lọt vào Qdrant.
"""
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Category = Literal[
    "thu-tuc",
    "hoc-bong-ren-luyen",
    "khen-thuong-ky-luat",
    "dao-tao",
    "hoc-phi",
    "lien-he",
]

SLUG = r"^[a-z0-9]+(-[a-z0-9]+)*$"


class DocumentMeta(BaseModel):
    """Front matter ở đầu mỗi file .md trong data/."""

    model_config = ConfigDict(extra="forbid")  # gõ sai tên trường -> báo lỗi

    doc_id: str = Field(pattern=SLUG)
    title: str = Field(min_length=3)
    category: Category
    document_number: str | None = None
    issued_date: date | None = None
    applies_to: str | None = None


class ChunkMeta(DocumentMeta):
    """Metadata của 1 chunk = metadata tài liệu + vị trí của chunk trong tài liệu."""

    source_file: str
    heading_path: str
    chunk_index: int = Field(ge=0)         # thứ tự trong tài liệu (đếm riêng cho cha và con)
    level: Literal["parent", "child"] = "child"
    parent_id: str | None = None           # chunk con trỏ về chunk cha; None = section ngắn, tự đủ nghĩa


class Chunk(BaseModel):
    """Đơn vị mà RAG tìm kiếm: 1 đoạn văn bản + metadata."""

    chunk_id: str = Field(pattern=r"^[a-z0-9-]+-p?\d{3}$")  # cha: ...-p012, con: ...-045
    text: str = Field(min_length=30)
    metadata: ChunkMeta

    @model_validator(mode="after")
    def _check_hierarchy(self):
        level, parent_id = self.metadata.level, self.metadata.parent_id
        if level == "parent" and parent_id is not None:
            raise ValueError("chunk cha không được có parent_id")
        if level == "parent" and "-p" not in self.chunk_id:
            raise ValueError("chunk cha phải có chunk_id dạng <doc_id>-pNNN")
        limit = 8000 if level == "parent" else 1500   # chặn chunker sinh chunk quá to
        if len(self.text) > limit:
            raise ValueError(f"{self.chunk_id}: text dài {len(self.text)} > {limit} ký tự")
        return self

    def to_payload(self) -> dict:
        """Dạng phẳng để lưu vào Qdrant (ngày -> chuỗi, bỏ trường rỗng)."""
        data = self.model_dump(mode="json", exclude_none=True)
        meta = data.pop("metadata")
        return {**data, **meta}