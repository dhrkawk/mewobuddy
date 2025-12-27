from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.db import get_connection
from server.models import Token, User

security = HTTPBearer(auto_error=False)


def create_token(user_id: str) -> Token:
    conn = get_connection()
    cur = conn.cursor()
    token_value = uuid.uuid4().hex
    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO tokens (token, user_id, created_at) VALUES (?, ?, ?)",
        (token_value, user_id, now),
    )
    conn.commit()
    conn.close()
    return Token(token=token_value, user_id=user_id, created_at=datetime.fromisoformat(now))


def get_user_by_token(token: str) -> Optional[User]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT u.id, u.email, u.created_at
        FROM tokens t
        JOIN users u ON u.id = t.user_id
        WHERE t.token = ?
        """,
        (token,),
    )
    row = cur.fetchone()
    if row:
        return User(id=row["id"], email=row["email"], created_at=datetime.fromisoformat(row["created_at"]))
    return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user
