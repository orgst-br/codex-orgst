from ninja import Router
from ninja.errors import HttpError

from .models import Document, DocumentVersion
from .schemas import (
    DocumentCreateIn,
    DocumentOut,
    DocumentVersionCreateIn,
    DocumentVersionOut,
)
from .services import add_version, can_view_document, create_document, list_documents

router = Router(tags=["docs"])


def _doc_out(doc: Document) -> dict:
    return {
        "id": doc.id,
        "title": doc.title,
        "slug": doc.slug,
        "summary": doc.summary,
        "visibility": doc.visibility,
        "project_id": doc.project_id,
        "tags": [{"id": t.id, "name": t.name} for t in doc.tags.all()],
        "created_by_id": doc.created_by_id,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
    }


@router.get("/docs", response=list[DocumentOut])
def api_list_docs(
    request,
    q: str | None = None,
    tag: str | None = None,
    project_id: int | None = None,
):
    if not request.user.is_authenticated:
        raise HttpError(401, "AUTH_REQUIRED")
    docs = list_documents(user=request.user, q=q, tag=tag, project_id=project_id)
    return [_doc_out(d) for d in docs]


@router.post("/docs", response=DocumentOut)
def api_create_doc(request, payload: DocumentCreateIn):
    if not request.user.is_authenticated:
        raise HttpError(401, "AUTH_REQUIRED")

    doc = create_document(
        title=payload.title,
        body_md=payload.body_md,
        created_by=request.user,
        summary=payload.summary,
        visibility=payload.visibility,
        tag_names=payload.tags,
        project_id=payload.project_id,
    )
    doc = Document.objects.prefetch_related("tags").get(id=doc.id)
    return _doc_out(doc)


@router.get("/docs/{doc_id}", response=DocumentOut)
def api_get_doc(request, doc_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "AUTH_REQUIRED")

    doc = Document.objects.prefetch_related("tags").filter(id=doc_id).first()
    if not doc:
        raise HttpError(404, "DOC_NOT_FOUND")
    if not can_view_document(request.user, doc):
        raise HttpError(403, "FORBIDDEN")

    return _doc_out(doc)


@router.get("/docs/{doc_id}/versions", response=list[DocumentVersionOut])
def api_list_versions(request, doc_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "AUTH_REQUIRED")

    doc = Document.objects.filter(id=doc_id).first()
    if not doc:
        raise HttpError(404, "DOC_NOT_FOUND")
    if not can_view_document(request.user, doc):
        raise HttpError(403, "FORBIDDEN")

    versions = DocumentVersion.objects.filter(document=doc).order_by("-version_number")
    return [
        {
            "id": v.id,
            "version_number": v.version_number,
            "authored_by_id": v.authored_by_id,
            "created_at": v.created_at,
        }
        for v in versions
    ]


@router.post("/docs/{doc_id}/versions", response=DocumentVersionOut)
def api_add_version(request, doc_id: int, payload: DocumentVersionCreateIn):
    if not request.user.is_authenticated:
        raise HttpError(401, "AUTH_REQUIRED")

    doc = Document.objects.filter(id=doc_id).first()
    if not doc:
        raise HttpError(404, "DOC_NOT_FOUND")
    if not can_view_document(request.user, doc):
        raise HttpError(403, "FORBIDDEN")

    v = add_version(document=doc, body_md=payload.body_md, authored_by=request.user)
    return {
        "id": v.id,
        "version_number": v.version_number,
        "authored_by_id": v.authored_by_id,
        "created_at": v.created_at,
    }
