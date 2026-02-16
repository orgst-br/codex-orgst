from datetime import datetime, date
from typing import List, Optional

from ninja import Schema


class SkillOut(Schema):
    id: int
    name: str
    category: str
    created_at: datetime


class UserSkillIn(Schema):
    skill_id: int
    level: int = 1
    years_exp: int = 0
    can_mentor: bool = False


class UserSkillOut(Schema):
    skill: SkillOut
    level: int
    years_exp: int
    can_mentor: bool


class MemberCardOut(Schema):
    id: int
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    roles: List[str]
    skills: List[str]  # nomes simples pra card


class MemberDetailOut(Schema):
    id: int
    email: str
    display_name: str
    avatar_url: Optional[str] = None

    birth_date: Optional[date] = None
    profession: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


    roles: List[str]
    skills: List[UserSkillOut]


class ProfilePatchIn(Schema):
    display_name: Optional[str] = None
    birth_date: Optional[date] = None
    profession: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
