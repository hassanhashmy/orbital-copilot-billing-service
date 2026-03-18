from unittest.mock import AsyncMock

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.clients.orbital_copilot import OrbitalCopilotClient
from app.core.dependencies import get_orbital_client
from app.main import app
from app.models.billing import Message, Report


@pytest.fixture
def mock_client():
    return AsyncMock(spec=OrbitalCopilotClient)


@pytest.fixture(autouse=True)
def _cleanup_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def sample_messages():
    return [
        Message(
            id=1000,
            timestamp="2024-04-29T02:08:29.375Z",
            text="Generate a Tenant Obligations Report for the new lease terms.",
            report_id=5392,
        ),
        Message(
            id=1001,
            timestamp="2024-04-29T03:25:03.613Z",
            text="test test",
        ),
    ]


@pytest.fixture
def sample_report():
    return Report(id=5392, name="Tenant Obligations Report", credit_cost=79)


@pytest.mark.asyncio
async def test_usage_returns_correct_structure(
    mock_client, sample_messages, sample_report
):
    """The response should have a top-level 'usage' array with the correct fields."""

    mock_client.fetch_current_period_messages.return_value = sample_messages
    mock_client.fetch_report_by_id.return_value = sample_report
    app.dependency_overrides[get_orbital_client] = lambda: mock_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/usage")

    assert response.status_code == 200
    data = response.json()
    assert "usage" in data
    assert len(data["usage"]) == 2


@pytest.mark.asyncio
async def test_report_message_uses_report_credits(
    mock_client, sample_messages, sample_report
):
    """Messages with a valid report should use the report's credit_cost and include report_name."""

    mock_client.fetch_current_period_messages.return_value = sample_messages
    mock_client.fetch_report_by_id.return_value = sample_report
    app.dependency_overrides[get_orbital_client] = lambda: mock_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/usage")

    item = response.json()["usage"][0]
    assert item["message_id"] == 1000
    assert item["credits_used"] == 79
    assert item["report_name"] == "Tenant Obligations Report"
    assert item["timestamp"] == "2024-04-29T02:08:29.375Z"


@pytest.mark.asyncio
async def test_text_message_omits_report_name(
    mock_client, sample_messages, sample_report
):
    """Messages without a report should omit report_name entirely."""

    mock_client.fetch_current_period_messages.return_value = sample_messages
    mock_client.fetch_report_by_id.return_value = sample_report
    app.dependency_overrides[get_orbital_client] = lambda: mock_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/usage")

    item = response.json()["usage"][1]
    assert item["message_id"] == 1001
    assert "report_name" not in item
    assert item["credits_used"] == 1.85


@pytest.mark.asyncio
async def test_404_report_falls_back_to_text_calculation(mock_client):
    """When the reports API returns 404, credits should be calculated from message text."""

    mock_client.fetch_current_period_messages.return_value = [
        Message(
            id=2000,
            timestamp="2024-05-01T00:00:00Z",
            text="test test",
            report_id=9999,
        ),
    ]
    mock_client.fetch_report_by_id.return_value = None
    app.dependency_overrides[get_orbital_client] = lambda: mock_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/usage")

    assert response.status_code == 200
    item = response.json()["usage"][0]
    assert "report_name" not in item
    assert item["credits_used"] == 1.85


@pytest.mark.asyncio
async def test_empty_messages_returns_empty_usage(mock_client):
    """An empty messages list should produce an empty usage array."""

    mock_client.fetch_current_period_messages.return_value = []
    app.dependency_overrides[get_orbital_client] = lambda: mock_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/usage")

    assert response.status_code == 200
    assert response.json() == {"usage": []}


@pytest.mark.asyncio
async def test_upstream_error_returns_502(mock_client):
    """Network failures to the upstream service should yield a 502 response."""

    mock_client.fetch_current_period_messages.side_effect = httpx.RequestError(
        "connection failed"
    )
    app.dependency_overrides[get_orbital_client] = lambda: mock_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/usage")

    assert response.status_code == 502
