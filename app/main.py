from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .models import ScenarioRequest
from .scenarios import build_events, build_users, expected_outcome
from .store import Store
from .target import TargetClient

app = FastAPI(title="Referral Security Lab", version="0.2.0")
templates = Jinja2Templates(directory="app/templates")
store = Store(os.getenv("DB_PATH", "./data/referral_lab.db"))
target = TargetClient()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "target_enabled": target.enabled()},
    )


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "target_environment": target.environment,
        "target_integration": target.enabled(),
    }


@app.get("/api/scenarios")
async def scenarios():
    return {
        "scenarios": [
            "legit-referral", "self-referral", "rapid-signups",
            "referral-replay", "shared-device", "shared-network",
            "referral-chain",
        ]
    }


@app.post("/api/runs")
async def create_run(payload: ScenarioRequest):
    run_id = uuid.uuid4().hex[:12]
    users = build_users(payload.users, payload.seed, payload.scenario)
    events = build_events(payload.scenario, users, payload.referral_code, payload.seed)

    result = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scenario": payload.scenario,
        "expected": expected_outcome(payload.scenario),
        "status": "generated",
        "users": [u.model_dump() for u in users],
        "events": [e.model_dump(mode="json") for e in events],
        "notes": [
            "Synthetic identities only.",
            "Target integration is restricted to staging/test.",
            "No disposable-mail, proxy rotation, CAPTCHA bypass, or stealth automation is used.",
        ],
    }

    if payload.submit_to_target:
        if not target.enabled():
            raise HTTPException(400, "Target submission is disabled unless TARGET_ENV is staging/test and SUBMIT_TO_TARGET=true.")
        try:
            observed = await target.submit(result["events"])
            result["observed"] = observed
            result["status"] = "submitted"
            decision = str(observed.get("decision", observed.get("status", ""))).lower()
            expected = result["expected"]
            if expected == "reward-eligible":
                result["result"] = "PASS" if decision in {"reward-issued", "eligible", "approved"} else "REVIEW"
            elif expected == "flag-or-reject":
                result["result"] = "PASS" if decision in {"blocked", "rejected", "flagged", "review"} else "FAIL"
            else:
                result["result"] = "REVIEW"
        except Exception as exc:
            raise HTTPException(502, detail=f"Target submission failed: {exc}") from exc

    store.save(result)
    return result


@app.get("/api/runs")
async def list_runs():
    return {"runs": store.list_recent()}


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    result = store.get(run_id)
    if not result:
        raise HTTPException(404, "Run not found")
    return result
