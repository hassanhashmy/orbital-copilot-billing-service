import asyncio

from app.clients.orbital_copilot import OrbitalCopilotClient
from app.models.billing import Message, MessageCreditUsage, Report, UsageResponse
from app.services.credit_calculator import calculate_credits


async def get_usage_data(client: OrbitalCopilotClient) -> UsageResponse:
    """
    Assemble the full usage report for the current billing period.

    Fetches all messages, resolves their associated reports concurrently,
    and calculates credits for each message.
    """
    messages = await client.fetch_current_period_messages()
    report_cache = await _build_report_cache(client, messages)
    usage_items = _build_usage_items(messages, report_cache)
    
    return UsageResponse(usage=usage_items)


async def _build_report_cache(
    client: OrbitalCopilotClient,
    messages: list[Message],
) -> dict[int, Report | None]:
    """
    Fetch all unique reports referenced by messages in a single concurrent batch.

    Returns a dict mapping report_id to its Report (or None if the upstream
    API returned 404 for that ID).
    """
    unique_report_ids = {msg.report_id for msg in messages if msg.report_id is not None}
    results = await asyncio.gather(
        *(client.fetch_report_by_id(rid) for rid in unique_report_ids)
    )

    return dict(zip(unique_report_ids, results))


def _build_usage_items(
    messages: list[Message],
    report_cache: dict[int, Report | None],
) -> list[MessageCreditUsage]:
    """
    Convert each message into a MessageCreditUsage with its credit cost.

    If a valid report exists for the message, uses the report's fixed
    credit_cost. Otherwise falls back to text-based credit calculation.
    """
    items = []
    for msg in messages:
        report = report_cache.get(msg.report_id) if msg.report_id else None
        if report:
            items.append(MessageCreditUsage(
                message_id=msg.id,
                timestamp=msg.timestamp,
                report_name=report.name,
                credits_used=report.credit_cost,
            ))
        else:
            items.append(MessageCreditUsage(
                message_id=msg.id,
                timestamp=msg.timestamp,
                credits_used=calculate_credits(msg.text),
            ))

    return items
