# Referral Security Lab

A defensive referral-fraud testing harness for **authorized staging/test environments**.

## What it does

- Generates synthetic test users and consistent device/network profiles.
- Runs predefined referral-abuse scenarios without using real disposable-mail providers or proxy-evasion infrastructure.
- Records expected vs observed outcomes from a target application's test adapter.
- Provides a small web dashboard/API for creating and inspecting test runs.
- Keeps scenarios deterministic and configurable for regression testing.

## Safety boundary

Set `TARGET_ENV=staging` unless you explicitly configure another authorized test environment. The included simulator uses synthetic identities and test-only email addresses such as `user-0001@example.test`.

The harness does **not** include IP-rotation, CAPTCHA bypass, stealth automation, or instructions for concealing automation from third-party services.

## Stack

- Python 3.12+
- FastAPI
- Pydantic
- SQLite
- Jinja2
- pytest

## Run

```bash
python -m venv .venv
# activate the virtualenv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Environment

```env
TARGET_BASE_URL=http://127.0.0.1:9000
TARGET_ENV=staging
DB_PATH=./data/referral_lab.db
```

By design, the application refuses to run target-integrated scenarios unless TARGET_ENV is `staging` or `test`.

## Included scenarios

- legit-referral
- self-referral
- rapid-signups
- referral-replay
- shared-device
- shared-network
- referral-chain
