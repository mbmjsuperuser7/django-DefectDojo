"""
prvis DefectDojo webhook handler
Receives finding notifications from DefectDojo
Routes to: GRC feed (Eramba/prvis-grc), TheHive (high/critical), Mem0 context rebuild
"""
import os
import json
import httpx
from fastapi import FastAPI, Request
import asyncio

app = FastAPI(title="prvis-dd-webhook")

GRC_URL   = os.getenv("GRC_URL", "")
HIVE_URL  = os.getenv("THEHIVE_URL", "http://thehive:9000")
HIVE_TOK  = os.getenv("THEHIVE_TOKEN", "")
MEM0_URL  = os.getenv("MEM0_URL", "http://mem0:4004")

@app.post("/webhook/finding")
async def finding_webhook(request: Request):
    body = await request.json()
    findings = body.get("findings", [body])

    for finding in findings:
        severity  = finding.get("severity", "Info")
        title     = finding.get("title", "Unknown")
        desc      = finding.get("description", "")
        customer  = finding.get("tags", [""])[0] if finding.get("tags") else ""

        tasks = []
        # Route high/critical to TheHive
        if severity in ("Critical", "High") and HIVE_TOK:
            tasks.append(create_hive_case(title, severity, desc))

        # Always notify GRC
        if GRC_URL:
            tasks.append(notify_grc(finding))

        # Trigger Mem0 context rebuild if customer tagged
        if customer and MEM0_URL:
            tasks.append(rebuild_context(customer, "new_finding"))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    return {"ok": True, "processed": len(findings)}

async def create_hive_case(title, severity, description):
    level_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(f"{HIVE_URL}/api/case",
            headers={"Authorization": f"Bearer {HIVE_TOK}"},
            json={
                "title": f"[DefectDojo] {title}",
                "description": description,
                "severity": level_map.get(severity, 2),
                "tags": ["defectdojo", "prvis-ai"],
                "flag": severity == "Critical",
                "status": "New"
            })

async def notify_grc(finding):
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(f"{GRC_URL}/api/v1/findings", json=finding)

async def rebuild_context(customer_id, reason):
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(f"{MEM0_URL}/v1/context/rebuild",
            json={"customer_id": customer_id, "reason": reason})

@app.get("/health")
async def health(): return {"status": "ok"}
