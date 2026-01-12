from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv, find_dotenv

# Load env vars before importing routes (so ADMIN_SECRET is available)
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    found = find_dotenv()
    if found:
        load_dotenv(found)
    else:
        load_dotenv()

from server.db import get_connection, init_db  # noqa: E402
from server.routes import router  # noqa: E402

app = FastAPI(title="MeowBuddy API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    _seed_notices()


app.include_router(router)


@app.get("/")
def root():
    index_path = Path(__file__).resolve().parent / "templates" / "index.html"
    return FileResponse(index_path)


def _seed_notices() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM notices")
    row = cur.fetchone()
    if row and row["cnt"] > 0:
        conn.close()
        return
    now = datetime.utcnow().isoformat()
    seed_data = [
        ("諛⑹넚 怨듭?", "?ㅻ뒛 諛?8?쒖뿉 ?쇱씠釉뚮? ?⑸땲?? 留롮씠 ?二쇱꽭??"),
        ("肄쒕씪蹂??덇퀬", "?ㅼ쓬 二?湲덉슂?? ?ㅻⅨ 踰꾪뒠踰꾩? 肄쒕씪蹂?諛⑹넚 ?덉젙?낅땲??"),
        ("援우쫰 ?곗?", "?덈줈??援우쫰媛 怨?異쒖떆?⑸땲?? 湲곕??댁＜?몄슂!"),
    ]
    for title, content in seed_data:
        notice_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO notices (id, vtuber_id, title, content, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (notice_id, "vtuber-1", title, content, now),
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
    )

