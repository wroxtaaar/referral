# Referral Security Lab

Authorized staging/test referral-abuse simulator.

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

The target adapter is intentionally limited to TARGET_ENV=staging or test and uses synthetic example.test identities.