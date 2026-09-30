from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ScenarioName = Literal[
    "legit-referral",
    "self-referral",
    "rapid-signups",
    "referral-replay",
    "shared-device",
    "shared-network",
    "referral-chain",
]


class UserProfile(BaseModel):
    user_id: str
    email: str
    name: str
    device_id: str
    network_id: str
    locale: str = "en-IN"
    timezone: str = "Asia/Kolkata"


class ScenarioRequest(BaseModel):
    scenario: ScenarioName
    referral_code: str = Field(min_length=1, max_length=128)
    users: int = Field(default=5, ge=1, le=100)
    seed: int = Field(default=42, ge=0, le=2_147_483_647)


class TestEvent(BaseModel):
    timestamp: datetime
    user_id: str
    event_type: str
    details: dict


class TestResult(BaseModel):
    run_id: str
    scenario: ScenarioName
    expected: str
    status: str
    users: list[UserProfile]
    events: list[TestEvent]
    notes: list[str]
