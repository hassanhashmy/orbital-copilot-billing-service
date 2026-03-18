from fastapi import APIRouter, Depends, HTTPException
import httpx

from app.clients.orbital_copilot import OrbitalCopilotClient
from app.core.dependencies import get_orbital_client
from app.models.billing import UsageResponse
from app.services.billing import get_usage_data

router = APIRouter()


@router.get("/usage", response_model_exclude_none=True)
async def get_usage(
    client: OrbitalCopilotClient = Depends(get_orbital_client),
) -> UsageResponse:
    """Returns credit usage data for every message in the current billing period."""
    try:
        return await get_usage_data(client)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, detail=f"Upstream service error: {exc.response.status_code}")
    except httpx.RequestError as exc:
        raise HTTPException(502, detail=f"Failed to reach upstream service: {exc}")
