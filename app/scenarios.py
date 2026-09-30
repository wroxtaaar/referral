from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from .models import ScenarioName, TestEvent, UserProfile


def build_users(count: int, seed: int, scenario: ScenarioName) -> list[UserProfile]:
    rng = random.Random(seed)
    names = ["Aarav", "Vivaan", "Aditya", "Ishaan", "Kabir", "Rohan", "Anaya", "Diya"]
    users: list[UserProfile] = []

    for idx in range(count):
        user_id = f"test-user-{idx + 1:04d}"
        email = f"{user_id}@example.test"

        if scenario == "shared-device":
            device_id = "test-device-shared"
        else:
            device_id = f"test-device-{rng.randint(1000, 9999)}"

        if scenario == "shared-network":
            network_id = "test-network-shared"
        else:
            network_id = f"test-network-{rng.randint(1000, 9999)}"

        users.append(
            UserProfile(
                user_id=user_id,
                email=email,
                name=f"{rng.choice(names)} Test",
                device_id=device_id,
                network_id=network_id,
            )
        )

    return users


def build_events(
    scenario: ScenarioName,
    users: list[UserProfile],
    referral_code: str,
    seed: int,
) -> list[TestEvent]:
    now = datetime.now(timezone.utc)
    rng = random.Random(seed)
    events: list[TestEvent] = []

    for idx, user in enumerate(users):
        if scenario == "rapid-signups":
            offset = timedelta(seconds=idx * 2)
        elif scenario == "legit-referral":
            offset = timedelta(hours=idx * 6 + 1)
        else:
            offset = timedelta(minutes=idx * 5 + 1)

        click_time = now + offset
        events.append(
            TestEvent(
                timestamp=click_time,
                user_id=user.user_id,
                event_type="referral_click",
                details={"referral_code": referral_code},
            )
        )

        events.append(
            TestEvent(
                timestamp=click_time + timedelta(seconds=rng.randint(5, 60)),
                user_id=user.user_id,
                event_type="signup",
                details={
                    "email": user.email,
                    "device_id": user.device_id,
                    "network_id": user.network_id,
                },
            )
        )

    if scenario == "referral-replay" and users:
        original = users[0]
        events.append(
            TestEvent(
                timestamp=now + timedelta(minutes=1),
                user_id=original.user_id,
                event_type="referral_replay",
                details={"referral_code": referral_code, "attempt": 2},
            )
        )

    if scenario == "self-referral" and len(users) >= 2:
        events.append(
            TestEvent(
                timestamp=now + timedelta(minutes=2),
                user_id=users[1].user_id,
                event_type="self_referral_candidate",
                details={
                    "referrer_user_id": users[0].user_id,
                    "shared_device": users[0].device_id == users[1].device_id,
                    "shared_network": users[0].network_id == users[1].network_id,
                },
            )
        )

    if scenario == "referral-chain" and len(users) >= 3:
        for idx in range(1, len(users)):
            events.append(
                TestEvent(
                    timestamp=now + timedelta(minutes=3 + idx),
                    user_id=users[idx].user_id,
                    event_type="referral_relationship",
                    details={
                        "referred_by": users[idx - 1].user_id,
                        "referral_code": referral_code,
                    },
                )
            )

    return events


def expected_outcome(scenario: ScenarioName) -> str:
    if scenario == "legit-referral":
        return "reward-eligible"
    if scenario in {"self-referral", "referral-replay", "shared-device", "shared-network"}:
        return "flag-or-reject"
    if scenario in {"rapid-signups", "referral-chain"}:
        return "risk-review"
    return "risk-review"
