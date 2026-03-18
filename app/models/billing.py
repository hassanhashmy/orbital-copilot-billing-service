from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    id: int
    timestamp: str
    text: str
    report_id: Optional[int] = None


class Report(BaseModel):
    id: int
    name: str
    credit_cost: int


class MessageCreditUsage(BaseModel):
    message_id: int
    timestamp: str
    report_name: Optional[str] = None
    credits_used: float


class UsageResponse(BaseModel):
    usage: list[MessageCreditUsage]
