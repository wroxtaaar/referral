from __future__ import annotations

import os
from typing import Any

import httpx


class TargetClient:
    """
    Optional adapter for an authorized staging/test target.

    The target endpoint is expected to expose a test-only contract:
      POST /api/referral-test/events
      body: {"events": [...]}

    This adapter deliberately requires TARGET_ENV=staging or test.
    """

    def __init__(self):
        self.base_url = os.getenv("TARGET_BASE_URL", "http://127.0.0.1:9000").rstrip("/")
        self.environment = os.getenv("TARGET_ENV", "staging").lower()

    def enabled(self) -> bool:
        return self.environment in {"staging", "test"}

    async def submit(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        if not self.enabled():
            raise RuntimeError("Target integration is disabled outside staging/test.")

        url = f"{self.base_url}/api/referral-test/events"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json={"events": events})
            response.raise_for_status()
            return response.json()
