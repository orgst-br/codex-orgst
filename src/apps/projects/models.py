from __future__ import annotations

from django.conf import settings
from django.db import models

from orgst.common.models import TimeStampedModel


class ProjectStatus(models.TextChoices):
    """Lifecycle de um projeto dentro da comunidade."""

    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    DONE = "done", "Done"


class Project(TimeStampedModel):
    """
    Projeto mínimo para permitir vincular Docs a um projeto.
    Fase 4 vai expandir (members, boards, tasks).
    """

    name = models.CharField(max_length=160, unique=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.ACTIVE
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects",
    )

    def __str__(self) -> str:
        return self.name
