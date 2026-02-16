from datetime import datetime
from typing import List, Optional

from ninja import Schema


class InvitationCreateIn(Schema):
    email: str
    role_keys: List[str]
    expires_in_days: int = 7


class InvitationCreateOut(Schema):
    id: str
    email: str
    status: str
    expires_at: datetime
    invite_token: str  # token puro (retornar só aqui)


class InvitationValidateOut(Schema):
    valid: bool
    email: Optional[str] = None
    role_keys: List[str] = []
    expires_at: Optional[datetime] = None


class InvitationAcceptIn(Schema):
    token: str
    password: str
    display_name: str


class InvitationAcceptOut(Schema):
    user_id: str
    email: str
