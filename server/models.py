from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: str
    email: str
    created_at: datetime


@dataclass
class Token:
    token: str
    user_id: str
    created_at: datetime
    last_used_at: Optional[datetime] = None
