from django.contrib import admin

<<<<<<< HEAD
from .models import Skill, UserSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "created_at")
    search_fields = ("name",)
    list_filter = ("category",)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "skill", "level", "years_exp", "can_mentor")
    list_filter = ("can_mentor", "level", "skill__category")
    search_fields = ("user__email", "skill__name")
=======
# Register your models here.
>>>>>>> 13000a6 (chore: setup inicial (Django/Ninja, settings por env, docker-compose Postgres))
