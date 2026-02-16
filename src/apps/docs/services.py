from __future__ import annotations

from collections.abc import Iterable

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max, Q
from django.utils.text import slugify

from apps.accounts.models import UserRole

from .models import Document, DocumentVersion, DocumentVisibility, Tag

User = get_user_model()


MENTOR_KEYS = {"mentor", "coach", "admin", "cofounder"}


def user_has_any_role(user: User, keys: set[str]) -> bool:
    """Retorna True se o usuário possuir algum role com key em `keys`."""
    if not user.is_authenticated:
        return False
    return UserRole.objects.filter(user=user, role__key__in=list(keys)).exists()


def can_view_document(user: User, doc: Document) -> bool:
    """Regra de visibilidade do documento."""
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    if doc.visibility == DocumentVisibility.COMMUNITY:
        return True
    if doc.visibility == DocumentVisibility.MENTORS_ONLY:
        return user_has_any_role(user, MENTOR_KEYS)
    # private
    return doc.created_by_id == user.id


def _unique_slug(base: str) -> str:
    """Garante slug único (base, base-2, base-3...)."""
    slug = base
    i = 2
    while Document.objects.filter(slug=slug).exists():
        slug = f"{base}-{i}"[:220]
        i += 1
    return slug


@transaction.atomic
def create_document(
    *,
    title: str,
    body_md: str,
    created_by: User,
    summary: str | None = None,
    visibility: str = DocumentVisibility.COMMUNITY,
    tag_names: Iterable[str] | None = None,
    project_id: int | None = None,
) -> Document:
    """
    Cria um Document e sua versão inicial (v1).
    """
    base = slugify(title)[:220] or "doc"
    slug = _unique_slug(base)

    doc = Document.objects.create(
        title=title,
        slug=slug,
        summary=summary,
        visibility=visibility,
        created_by=created_by,
        project_id=project_id,
    )

    DocumentVersion.objects.create(
        document=doc,
        version_number=1,
        body_md=body_md,
        authored_by=created_by,
    )

    if tag_names:
        tags = []
        for name in tag_names:
            n = name.strip()
            if not n:
                continue
            tag, _ = Tag.objects.get_or_create(name=n)
            tags.append(tag)
        doc.tags.add(*tags)

    return doc


@transaction.atomic
def add_version(
    *, document: Document, body_md: str, authored_by: User
) -> DocumentVersion:
    """
    Adiciona uma nova versão ao documento.
    Usa lock implícito via transação + agregação do max.
    """
    last = (
        DocumentVersion.objects.filter(document=document)
        .aggregate(m=Max("version_number"))
        .get("m")
        or 0
    )
    next_version = last + 1
    return DocumentVersion.objects.create(
        document=document,
        version_number=next_version,
        body_md=body_md,
        authored_by=authored_by,
    )


def list_documents(
    *, user: User, q: str | None, tag: str | None, project_id: int | None
):
    """
    Lista documentos aplicando filtros e respeitando visibilidade.
    (MVP: filtro por visibilidade no Python/Query simples; depois refinamos).
    """
    qs = (
        Document.objects.select_related("created_by", "project")
        .prefetch_related("tags")
        .order_by("-created_at")
    )

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))
    if project_id:
        qs = qs.filter(project_id=project_id)
    if tag:
        qs = qs.filter(tags__name__iexact=tag)

    # aplica visibilidade
    docs = [d for d in qs if can_view_document(user, d)]
    return docs
