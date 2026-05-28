"""
Validation Agent – Autonomously validates MAP completion by checking audit logs and evidence.
"""
from datetime import datetime
from database.db import get_db_session
from sqlalchemy import text
from loguru import logger


class ValidationAgent:
    """Validates whether a MAP has been completed with sufficient evidence."""

    async def validate(self, map_id: int) -> dict:
        """Run validation checks on a MAP."""
        async with get_db_session() as db:
            # Fetch MAP
            row = (await db.execute(
                text("SELECT * FROM maps WHERE id=:id"), {"id": map_id}
            )).fetchone()
            if not row:
                return {"success": False, "error": "MAP not found"}

            cols = ["id", "regulation_id", "title", "description", "priority",
                    "department", "deadline", "status", "evidence_url", "created_at", "updated_at"]
            m = dict(zip(cols, row))

            checks = []
            passed = 0

            # ── Check 1: Status must be 'completed' ──────────────────────
            if m["status"] == "completed":
                checks.append({"check": "Status is 'completed'", "passed": True})
                passed += 1
            else:
                checks.append({"check": "Status is 'completed'", "passed": False,
                                "reason": f"Current status: {m['status']}"})

            # ── Check 2: Audit log must have at least 1 action ───────────
            log_count = (await db.execute(
                text("SELECT COUNT(*) FROM audit_logs WHERE map_id=:id"), {"id": map_id}
            )).scalar()
            if log_count > 0:
                checks.append({"check": "Audit trail exists", "passed": True,
                                "detail": f"{log_count} log entries found"})
                passed += 1
            else:
                checks.append({"check": "Audit trail exists", "passed": False,
                                "reason": "No audit log entries found"})

            # ── Check 3: Evidence URL or notes ───────────────────────────
            evidence_log = (await db.execute(
                text("SELECT notes FROM audit_logs WHERE map_id=:id AND action LIKE '%Evidence%'"), {"id": map_id}
            )).fetchone()
            has_evidence = bool(m["evidence_url"]) or bool(evidence_log)
            if has_evidence:
                checks.append({"check": "Evidence documented", "passed": True})
                passed += 1
            else:
                checks.append({"check": "Evidence documented", "passed": False,
                                "reason": "No evidence URL or evidence log found"})

            # ── Check 4: Deadline not breached for critical items ─────────
            if m["deadline"]:
                deadline_dt = datetime.strptime(m["deadline"], "%Y-%m-%d")
                if m["status"] == "completed" or datetime.utcnow() <= deadline_dt:
                    checks.append({"check": "Deadline compliance", "passed": True})
                    passed += 1
                else:
                    checks.append({"check": "Deadline compliance", "passed": False,
                                   "reason": f"Deadline {m['deadline']} was breached"})
            else:
                checks.append({"check": "Deadline compliance", "passed": True, "detail": "No deadline set"})
                passed += 1

            total = len(checks)
            validation_score = round((passed / total) * 100, 1)
            overall = validation_score >= 75

            # Log validation
            await db.execute(
                text("INSERT INTO audit_logs (map_id, action, actor, timestamp, notes) VALUES (:mid, :act, :actor, :ts, :notes)"),
                {
                    "mid": map_id,
                    "act": "Validation Run",
                    "actor": "ValidationAgent",
                    "ts": datetime.utcnow().isoformat(),
                    "notes": f"Score: {validation_score}% ({passed}/{total} checks passed). {'APPROVED' if overall else 'FAILED'}",
                },
            )

            # If fully validated, mark as completed
            if overall and m["status"] != "completed":
                await db.execute(
                    text("UPDATE maps SET status='completed', updated_at=:now WHERE id=:id"),
                    {"now": datetime.utcnow().isoformat(), "id": map_id},
                )
                # Resolve existing alerts
                await db.execute(
                    text("UPDATE alerts SET resolved=1 WHERE map_id=:id"), {"id": map_id}
                )

            await db.commit()
            logger.info(f"✅ Validated MAP #{map_id} – Score: {validation_score}%")

            return {
                "map_id": map_id,
                "title": m["title"],
                "validation_score": validation_score,
                "overall_passed": overall,
                "checks": checks,
                "timestamp": datetime.utcnow().isoformat(),
            }
