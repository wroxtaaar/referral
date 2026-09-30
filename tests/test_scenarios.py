from app.scenarios import build_events, build_users, expected_outcome


def test_shared_device():
    users = build_users(5, 42, "shared-device")
    assert len({u.device_id for u in users}) == 1


def test_shared_network():
    users = build_users(5, 42, "shared-network")
    assert len({u.network_id for u in users}) == 1


def test_users_are_synthetic():
    users = build_users(3, 42, "legit-referral")
    assert all(u.email.endswith("@example.test") for u in users)


def test_replay_event():
    users = build_users(2, 42, "referral-replay")
    events = build_events("referral-replay", users, "TEST", 42)
    assert any(e.event_type == "referral_replay" for e in events)


def test_expectations():
    assert expected_outcome("legit-referral") == "reward-eligible"
    assert expected_outcome("shared-device") == "flag-or-reject"
    assert expected_outcome("referral-replay") == "flag-or-reject"
