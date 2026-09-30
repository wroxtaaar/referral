from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .models import ScenarioRequest
from .scenarios import build_events, build_users, expected_outcome
from .store import Store
from .target import TargetClient

app = FastAPI(title="Referral Security Lab", version="0.1.0")
templates = Jinja2Templates(directory="app/templates")

store = Store(os.getenv("DB_PATH", "./data/referral_lab.db"))
target = TargetClient()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    runs = store.list_recent()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "runs": runs, "target_enabled": target.enabled()},
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
            "legit-referral",
            "self-referral",
            "rapid-signups",
            "referral-replay",
            "shared-device",
            "shared-network",
            "referral-chain",
        ]
    }


@app.post("/api/runs")
async def create_run(payload: ScenarioRequest):
    run_id = uuid.uuid4().hex[:12]
    users = build_users(payload.users, payload.seed, payload.scenario)
    events = build_events(
        payload.scenario,
        users,
        payload.referral_code,
        payload.seed,
    )

    result = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scenario": payload.scenario,
        "expected": expected_outcome(payload.scenario),
        "status": "generated",
        "users": [u.model_dump() for u in users],
        "events": [e.model_dump(mode="json") for e in events],
        "notes": [
            "Synthetic test identities only.",
            "No real disposable-mail or IP-rotation service is used.",
        ],
    }

    if os.getenv("SUBMIT_TO_TARGET", "false").lower() == "true":
        try:
            observed = await target.submit(result["events"])
            result["status"] = "submitted"
            result["observed"] = observed
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Target submission failed: {exc}") from exc

    store.save(result)
    return result


@app.get("/api/runs")
async def list_runs():
    return {"runs": store.list_recent()}


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    result = store.get(run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Run not found")
    return result
