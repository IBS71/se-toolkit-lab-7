"""
LMS API Client — HTTP client for the LMS backend.
"""

import httpx
from typing import Optional, Any


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_items(self) -> list[dict[str, Any]]:
        client = await self._get_client()
        resp = await client.get(f"{self.base_url}/items/")
        resp.raise_for_status()
        return resp.json()

    async def get_analytics(
        self, endpoint: str, lab: Optional[str] = None, limit: Optional[int] = None
    ) -> dict[str, Any]:
        client = await self._get_client()
        params = {"lab": lab} if lab else {}
        if limit:
            params["limit"] = limit
        resp = await client.get(
            f"{self.base_url}/analytics/{endpoint}", params=params
        )
        resp.raise_for_status()
        return resp.json()

    async def health_check(self) -> dict[str, Any]:
        try:
            items = await self.get_items()
            return {"healthy": True, "item_count": len(items)}
        except httpx.ConnectError as e:
            return {"healthy": False, "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {
                "healthy": False,
                "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}",
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
