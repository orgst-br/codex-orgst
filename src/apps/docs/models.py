from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from orgst.common.models import TimeStampedModel


class DocumentVisibility(models.TextChoices):
    """Níveis de visibilidade de um documento."""

    COMMUNITY = "community", "Community"
    MENTORS_ONLY = "mentors_only", "Mentors only"
    PRIVATE = "private", "Private"


class Tag(TimeStampedModel):
    """Tag simples para categorizar documentos."""

    name = models.CharField(max_length=60, unique=True)

    def __str__(self) -> str:
        return self.name


class Document(TimeStampedModel):
    """
    Documento com metadados. O conteúdo markdown é versionado em DocumentVersion.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField(null=True, blank=True)

    visibility = models.CharField(
        max_length=20,
        choices=DocumentVisibility.choices,
        default=DocumentVisibility.COMMUNITY,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_documents",
    )

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )

    tags = models.ManyToManyField(Tag, through="DocumentTag", related_name="documents")

    class Meta:
        indexes = [
            models.Index(fields=["visibility", "created_at"]),
            models.Index(fields=["project", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def build_slug(title: str) -> str:
        """Gera um slug base a partir do título."""
        return slugify(title)[:220] or "doc"


class DocumentVersion(TimeStampedModel):
    """
    Versão do conteúdo do documento. Somente body_md é versionado.
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="versions"
    )
    version_number = models.PositiveIntegerField()
    body_md = models.TextField()

    authored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="authored_document_versions",
    )

    class Meta:
        unique_together = [("document", "version_number")]
        indexes = [models.Index(fields=["document", "version_number"])]

    def __str__(self) -> str:
        return f"{self.document_id}@v{self.version_number}"


class DocumentTag(models.Model):
    """Tabela de junção N:N entre Document e Tag."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("document", "tag")]
