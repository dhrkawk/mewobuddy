from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
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
        ("방송 공지", "오늘 밤 8시에 라이브를 합니다! 많이 와주세요."),
        ("콜라보 예고", "다음 주 금요일, 다른 버튜버와 콜라보 방송 예정입니다."),
        ("굿즈 티저", "새로운 굿즈가 곧 출시됩니다. 기대해주세요!"),
    ]
    for title, content in seed_data:
        notice_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO notices (id, vtuber_id, title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (notice_id, "vtuber-1", title, content, now),
        )
    conn.commit()
    conn.close()


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>MeowBuddy Admin - Notices</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 0 auto; padding: 20px; }
    label { display: block; margin-top: 10px; font-weight: bold; }
    input, textarea { width: 100%; padding: 8px; margin-top: 4px; }
    button { margin-top: 12px; padding: 10px 16px; cursor: pointer; }
    .status { margin-top: 10px; }
    .notice { border: 1px solid #ddd; padding: 10px; margin-top: 10px; }
    .error { color: red; }
    .success { color: green; }
  </style>
</head>
<body>
  <h1>MeowBuddy Admin - Notices</h1>
  <div>
    <label for="secret">Admin Secret</label>
    <input id="secret" type="password" placeholder="Enter admin secret" />

    <label for="title">Title</label>
    <input id="title" type="text" />

    <label for="content">Content</label>
    <textarea id="content" rows="6"></textarea>

    <button onclick="publish()">Publish</button>
    <div id="status" class="status"></div>
  </div>

  <h2>Latest Notices</h2>
  <div id="notices"></div>

  <script>
    async function publish() {
      const secret = document.getElementById('secret').value;
      const title = document.getElementById('title').value;
      const content = document.getElementById('content').value;
      const statusEl = document.getElementById('status');
      statusEl.textContent = 'Publishing...';
      statusEl.className = 'status';
      try {
        const resp = await fetch('/admin/notices', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Admin-Secret': secret
          },
          body: JSON.stringify({ title, content })
        });
        if (!resp.ok) {
          const txt = await resp.text();
          throw new Error(txt || resp.statusText);
        }
        statusEl.textContent = 'Published!';
        statusEl.className = 'status success';
        document.getElementById('title').value = '';
        document.getElementById('content').value = '';
        loadNotices(secret);
      } catch (err) {
        statusEl.textContent = 'Failed: ' + err;
        statusEl.className = 'status error';
      }
    }

    async function loadNotices(secret) {
      const container = document.getElementById('notices');
      container.textContent = 'Loading...';
      try {
        const resp = await fetch('/admin/notices', {
          headers: { 'X-Admin-Secret': secret }
        });
        if (!resp.ok) throw new Error(await resp.text());
        const data = await resp.json();
        if (!data.length) {
          container.textContent = 'No notices yet.';
          return;
        }
        container.innerHTML = '';
        data.forEach(n => {
          const div = document.createElement('div');
          div.className = 'notice';
          div.innerHTML = '<strong>' + n.title + '</strong><br/>' +
            '<small>' + n.created_at + '</small><br/>' +
            '<div>' + n.content + '</div>';
          container.appendChild(div);
        });
      } catch (err) {
        container.textContent = 'Failed to load notices: ' + err;
      }
    }

    document.getElementById('secret').addEventListener('blur', (e) => {
      const secret = e.target.value;
      if (secret) loadNotices(secret);
    });
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
    )
