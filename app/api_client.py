from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from app.settings import get_api_base_url


class ApiClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.base_url = get_api_base_url().rstrip("/")
        self.token = token

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, email: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def me(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/me",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def set_token(self, token: Optional[str]) -> None:
        self.token = token

    def get_notices(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/notices",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
