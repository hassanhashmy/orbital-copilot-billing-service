from collections.abc import AsyncGenerator

import httpx

from app.clients.orbital_copilot import OrbitalCopilotClient


async def get_orbital_client() -> AsyncGenerator[OrbitalCopilotClient, None]:
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        yield OrbitalCopilotClient(http_client)
