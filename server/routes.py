from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Header, status

from server.auth import create_token, get_current_user
from server.db import get_connection
from server.models import User
import os

def _admin_secret() -> str:
    return os.getenv("ADMIN_SECRET", "")

router = APIRouter()


@router.post("/auth/login")
def login(payload: Dict[str, str]):
    email = (payload.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email, created_at FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        user_id = row["id"]
    else:
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO users (id, email, created_at) VALUES (?, ?, ?)",
            (user_id, email, now),
        )
        conn.commit()
    conn.close()

    token = create_token(user_id)
    return {"access_token": token.token, "user_id": token.user_id}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "equipped_items": [],
    }


@router.get("/notices")
def list_notices(current_user: User = Depends(get_current_user)):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, content, created_at FROM notices ORDER BY created_at DESC"
        )
        rows = cur.fetchall()
        return [
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    finally:
        conn.close()


def _require_admin(secret: str):
    admin_secret = _admin_secret()
    if not admin_secret or secret != admin_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin secret")


@router.post("/admin/notices")
def admin_create_notice(
    payload: Dict[str, str],
    x_admin_secret: str = Header(None),
):
    _require_admin(x_admin_secret or "")
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    if not title or not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title and content are required")
    conn = get_connection()
    try:
        cur = conn.cursor()
        notice_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        vtuber_id = payload.get("vtuber_id") or "vtuber-1"
        cur.execute(
            """
            INSERT INTO notices (id, vtuber_id, title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (notice_id, vtuber_id, title, content, now),
        )
        conn.commit()
        return {"id": notice_id, "title": title, "content": content, "created_at": now}
    finally:
        conn.close()


@router.get("/admin/notices")
def admin_list_notices(x_admin_secret: str = Header(None)):
    _require_admin(x_admin_secret or "")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, content, created_at FROM notices ORDER BY created_at DESC LIMIT 20"
        )
        rows = cur.fetchall()
        return [
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    finally:
        conn.close()


@router.post("/notices")
def create_notice(payload: Dict[str, str]):
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    if not title or not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title and content are required")
    conn = get_connection()
    try:
        cur = conn.cursor()
        notice_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        vtuber_id = payload.get("vtuber_id") or "vtuber-1"
        cur.execute(
            """
            INSERT INTO notices (id, vtuber_id, title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (notice_id, vtuber_id, title, content, now),
        )
        conn.commit()
        return {"id": notice_id, "created_at": now}
    finally:
        conn.close()
