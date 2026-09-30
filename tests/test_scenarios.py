from app.scenarios import build_users, expected_outcome

def test_shared_device():
    users=build_users(5,42,'shared-device')
    assert len({u.device_id for u in users})==1

def test_shared_network():
    users=build_users(5,42,'shared-network')
    assert len({u.network_id for u in users})==1

def test_legit_expectation():
    assert expected_outcome('legit-referral')=='reward-eligible'
