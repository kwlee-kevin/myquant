from __future__ import annotations

from typing import Any

import requests


def _safe_response_snippet(response: requests.Response, limit: int = 500) -> str:
    try:
        text = (response.text or "").strip()
    except Exception:
        text = ""
    return text[:limit]


class KiwoomClient:
    def __init__(self, base_url: str, app_key: str, app_secret: str, timeout: int = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_key = app_key
        self.app_secret = app_secret
        self.timeout = timeout

    def issue_token(self) -> dict[str, Any]:
        url = f"{self.base_url}/oauth2/token"
        headers = {
            "Content-Type": "application/json",
            "api-id": "au10001",
        }
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        if not response.ok:
            snippet = _safe_response_snippet(response)
            raise requests.HTTPError(
                f"Kiwoom token HTTP error status={response.status_code} url={url} body={snippet}",
                response=response,
            )
        data = response.json()

        token_type = data.get("token_type")
        token = data.get("token")
        if not token_type or not token:
            raise ValueError("Kiwoom token response missing token_type or token")

        return data

    def fetch_stock_list(self, token_type: str, token: str, mrkt_tp: str) -> list[dict[str, Any]]:
        url = f"{self.base_url}/api/dostk/stkinfo"
        headers = {
            "Content-Type": "application/json",
            "authorization": f"{token_type} {token}",
            "api-id": "ka10099",
        }
        payload = {"mrkt_tp": str(mrkt_tp)}
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        if not response.ok:
            snippet = _safe_response_snippet(response)
            raise requests.HTTPError(
                f"Kiwoom list HTTP error status={response.status_code} url={url} body={snippet}",
                response=response,
            )
        data = response.json()
        return self._extract_items(data)

    @staticmethod
    def _extract_items(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]

        if not isinstance(data, dict):
            return []

        preferred_keys = ["items", "data", "list", "output", "stkinfo"]
        for key in preferred_keys:
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

        for value in data.values():
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value

        return []
