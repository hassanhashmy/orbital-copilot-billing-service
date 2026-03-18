from typing import Optional

import httpx

from app.core.config import ORBITAL_COPILOT_BASE_URL
from app.models.billing import Message, Report


class OrbitalCopilotClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = ORBITAL_COPILOT_BASE_URL.rstrip("/")

    async def _get(self, endpoint: str) -> httpx.Response:
        return await self.client.get(f"{self.base_url}{endpoint}")

    async def fetch_current_period_messages(self) -> list[Message]:
        """Fetch all messages for the current billing period."""

        response = await self._get("/messages/current-period")
        response.raise_for_status()
        data = response.json()

        return [Message(**msg) for msg in data.get("messages", [])]

    async def fetch_report_by_id(self, report_id: int) -> Optional[Report]:
        """
        Fetch a report by ID. Returns None if the report is not found (404),
        allowing the caller to fall back to text-based credit calculation.
        """

        response = await self._get(f"/reports/{report_id}")

        if response.status_code == 404:
            report = None
        else:
            response.raise_for_status()
            report = Report(**response.json())

        return report
