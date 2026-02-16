from datetime import datetime

from ninja import Schema


class TagOut(Schema):
    id: int
    name: str


class DocumentOut(Schema):
    id: int
    title: str
    slug: str
    summary: str | None = None
    visibility: str
    project_id: int | None = None
    tags: list[TagOut]
    created_by_id: int
    created_at: datetime
    updated_at: datetime


class DocumentCreateIn(Schema):
    title: str
    summary: str | None = None
    visibility: str = "community"
    project_id: int | None = None
    tags: list[str] = []
    body_md: str


class DocumentVersionOut(Schema):
    id: int
    version_number: int
    authored_by_id: int
    created_at: datetime


class DocumentVersionCreateIn(Schema):
    body_md: str
