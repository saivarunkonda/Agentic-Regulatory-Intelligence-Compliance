"""
SuRaksha – Agentic Regulatory Intelligence & Compliance
FastAPI Backend Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uvicorn

from database.db import init_db, get_db_session
from agents.ingestion_agent import IngestionAgent
from agents.nlp_agent import NLPAgent
from agents.routing_agent import RoutingAgent
from agents.validation_agent import ValidationAgent
from services.scraper import RegulationScraper
from models.map_model import MAPCreate, MAPUpdate, MAPStatus
from models.department_model import DepartmentUpdate

# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("[OK] SuRaksha API started - DB initialized")
    yield

# ── App Init ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SuRaksha API",
    description="Agentic Regulatory Intelligence & Compliance System – Canara Bank",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Agents ───────────────────────────────────────────────────────────────────
ingestion_agent = IngestionAgent()
nlp_agent = NLPAgent()
routing_agent = RoutingAgent()
validation_agent = ValidationAgent()


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """Returns KPI summary for the dashboard."""
    async with get_db_session() as db:
        from sqlalchemy import text
        stats = {}

        stats["total_regulations"] = (await db.execute(text("SELECT COUNT(*) FROM regulations"))).scalar()
        stats["total_maps"] = (await db.execute(text("SELECT COUNT(*) FROM maps"))).scalar()
        stats["pending_maps"] = (await db.execute(text("SELECT COUNT(*) FROM maps WHERE status='pending'"))).scalar()
        stats["in_progress_maps"] = (await db.execute(text("SELECT COUNT(*) FROM maps WHERE status='in_progress'"))).scalar()
        stats["completed_maps"] = (await db.execute(text("SELECT COUNT(*) FROM maps WHERE status='completed'"))).scalar()
        stats["overdue_maps"] = (await db.execute(text(
            "SELECT COUNT(*) FROM maps WHERE status != 'completed' AND deadline < date('now')"
        ))).scalar()
        stats["active_alerts"] = (await db.execute(text("SELECT COUNT(*) FROM alerts WHERE resolved=0"))).scalar()

        total = stats["total_maps"] or 1
        stats["compliance_score"] = round((stats["completed_maps"] / total) * 100, 1)

        # Department breakdown
        dept_rows = (await db.execute(text(
            "SELECT department, COUNT(*) as cnt, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done FROM maps GROUP BY department"
        ))).fetchall()
        stats["department_breakdown"] = [
            {"department": r[0], "total": r[1], "completed": r[2], "score": round((r[2] / r[1]) * 100, 1)}
            for r in dept_rows
        ]

        # Recent regulations
        recent_regs = (await db.execute(text(
            "SELECT id, title, source, created_at FROM regulations ORDER BY created_at DESC LIMIT 5"
        ))).fetchall()
        stats["recent_regulations"] = [
            {"id": r[0], "title": r[1], "source": r[2], "created_at": str(r[3])}
            for r in recent_regs
        ]

        return stats


# ═══════════════════════════════════════════════════════════════════════════
# REGULATIONS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/regulations", tags=["Regulations"])
async def list_regulations(source: Optional[str] = None, limit: int = 50):
    async with get_db_session() as db:
        from sqlalchemy import text
        query = "SELECT * FROM regulations"
        params = {}
        if source:
            query += " WHERE source = :source"
            params["source"] = source
        query += " ORDER BY created_at DESC LIMIT :limit"
        params["limit"] = limit
        rows = (await db.execute(text(query), params)).fetchall()
        cols = ["id", "title", "source", "url", "raw_text", "status", "created_at"]
        return [dict(zip(cols, r)) for r in rows]


@app.post("/regulations/ingest", tags=["Regulations"])
async def ingest_regulations(background_tasks: BackgroundTasks):
    """Trigger real-time ingestion from regulatory feeds."""
    background_tasks.add_task(ingestion_agent.run_ingestion_cycle)
    return {"message": "Ingestion started in background", "status": "running"}


@app.post("/regulations/ingest/text", tags=["Regulations"])
async def ingest_from_text(payload: dict):
    """Ingest a regulation from raw text (for demo)."""
    title = payload.get("title", "Manual Entry")
    source = payload.get("source", "Manual")
    text_content = payload.get("text", "")
    reg_id = await ingestion_agent.ingest_text(title, source, text_content)
    return {"id": reg_id, "message": "Regulation ingested successfully"}


@app.post("/regulations/ingest/file", tags=["Regulations"])
async def ingest_from_file(file: UploadFile = File(...)):
    """Upload a PDF regulation document."""
    content = await file.read()
    reg_id = await ingestion_agent.ingest_pdf(file.filename, content)
    return {"id": reg_id, "message": f"PDF '{file.filename}' ingested successfully"}


# ═══════════════════════════════════════════════════════════════════════════
# MAPs – Measurable Action Points
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/maps", tags=["MAPs"])
async def list_maps(
    department: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
):
    async with get_db_session() as db:
        from sqlalchemy import text
        query = "SELECT * FROM maps WHERE 1=1"
        params = {}
        if department:
            query += " AND department = :department"
            params["department"] = department
        if status:
            query += " AND status = :status"
            params["status"] = status
        if priority:
            query += " AND priority = :priority"
            params["priority"] = priority
        query += " ORDER BY created_at DESC LIMIT :limit"
        params["limit"] = limit
        rows = (await db.execute(text(query), params)).fetchall()
        cols = ["id", "regulation_id", "title", "description", "priority", "department", "deadline", "status", "evidence_url", "created_at", "updated_at"]
        return [dict(zip(cols, r)) for r in rows]


@app.get("/maps/{map_id}", tags=["MAPs"])
async def get_map(map_id: int):
    async with get_db_session() as db:
        from sqlalchemy import text
        row = (await db.execute(text("SELECT * FROM maps WHERE id = :id"), {"id": map_id})).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="MAP not found")
        cols = ["id", "regulation_id", "title", "description", "priority", "department", "deadline", "status", "evidence_url", "created_at", "updated_at"]
        result = dict(zip(cols, row))
        # Audit log
        logs = (await db.execute(text("SELECT * FROM audit_logs WHERE map_id = :id ORDER BY timestamp DESC"), {"id": map_id})).fetchall()
        log_cols = ["id", "map_id", "action", "actor", "timestamp", "notes"]
        result["audit_logs"] = [dict(zip(log_cols, l)) for l in logs]
        return result


@app.post("/maps/generate/{regulation_id}", tags=["MAPs"])
async def generate_maps(regulation_id: int):
    """Generate MAPs from a regulation using NLP agent."""
    async with get_db_session() as db:
        from sqlalchemy import text
        reg = (await db.execute(text("SELECT * FROM regulations WHERE id = :id"), {"id": regulation_id})).fetchone()
        if not reg:
            raise HTTPException(status_code=404, detail="Regulation not found")
    maps = await nlp_agent.generate_maps(regulation_id, reg[4])  # raw_text
    routed = await routing_agent.assign_departments(maps)
    return {"maps_generated": len(routed), "maps": routed}


@app.patch("/maps/{map_id}/status", tags=["MAPs"])
async def update_map_status(map_id: int, update: MAPUpdate):
    async with get_db_session() as db:
        from sqlalchemy import text
        await db.execute(
            text("UPDATE maps SET status=:status, updated_at=:now WHERE id=:id"),
            {"status": update.status, "now": datetime.utcnow().isoformat(), "id": map_id},
        )
        await db.execute(
            text("INSERT INTO audit_logs (map_id, action, actor, timestamp, notes) VALUES (:mid, :act, :actor, :ts, :notes)"),
            {"mid": map_id, "act": f"Status → {update.status}", "actor": update.actor or "System", "ts": datetime.utcnow().isoformat(), "notes": update.notes or ""},
        )
        await db.commit()
    return {"message": "Status updated", "map_id": map_id, "new_status": update.status}


# ═══════════════════════════════════════════════════════════════════════════
# DEPARTMENTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/departments", tags=["Departments"])
async def list_departments():
    async with get_db_session() as db:
        from sqlalchemy import text
        rows = (await db.execute(text("SELECT * FROM departments"))).fetchall()
        cols = ["id", "name", "head", "contact", "compliance_score"]
        depts = [dict(zip(cols, r)) for r in rows]
        # Attach MAPs count per department
        for d in depts:
            counts = (await db.execute(text(
                "SELECT status, COUNT(*) FROM maps WHERE department=:dept GROUP BY status"
            ), {"dept": d["name"]})).fetchall()
            d["map_counts"] = {c[0]: c[1] for c in counts}
        return depts


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/validate/{map_id}", tags=["Validation"])
async def validate_map(map_id: int):
    """Trigger autonomous validation of a MAP."""
    result = await validation_agent.validate(map_id)
    return result


# ═══════════════════════════════════════════════════════════════════════════
# ALERTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/alerts", tags=["Alerts"])
async def get_alerts(resolved: bool = False):
    async with get_db_session() as db:
        from sqlalchemy import text
        rows = (await db.execute(text(
            "SELECT * FROM alerts WHERE resolved=:r ORDER BY created_at DESC"
        ), {"r": 1 if resolved else 0})).fetchall()
        cols = ["id", "map_id", "type", "message", "created_at", "resolved"]
        return [dict(zip(cols, r)) for r in rows]


@app.patch("/alerts/{alert_id}/resolve", tags=["Alerts"])
async def resolve_alert(alert_id: int):
    async with get_db_session() as db:
        from sqlalchemy import text
        await db.execute(text("UPDATE alerts SET resolved=1 WHERE id=:id"), {"id": alert_id})
        await db.commit()
    return {"message": "Alert resolved"}


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
