"""
Routing Agent – Assigns MAPs to correct bank departments and notifies them.
"""
from typing import List, Dict
from database.db import get_db_session
from sqlalchemy import text
from loguru import logger


class RoutingAgent:
    """Routes MAPs to departments and updates compliance scores."""

    async def assign_departments(self, maps: List[Dict]) -> List[Dict]:
        """Validate and confirm department assignments for a list of MAPs."""
        async with get_db_session() as db:
            for m in maps:
                dept = m.get("department", "Operations")
                # Ensure department exists
                exists = (await db.execute(
                    text("SELECT id FROM departments WHERE name=:name"), {"name": dept}
                )).fetchone()
                if not exists:
                    dept = "Operations"
                    await db.execute(
                        text("UPDATE maps SET department=:dept WHERE id=:id"),
                        {"dept": dept, "id": m["id"]},
                    )
                    m["department"] = dept

                # Log routing action
                await db.execute(
                    text("INSERT INTO audit_logs (map_id, action, actor, timestamp, notes) VALUES (:mid, :act, :actor, datetime('now'), :notes)"),
                    {
                        "mid": m["id"],
                        "act": f"Routed to {dept}",
                        "actor": "RoutingAgent",
                        "notes": f"Auto-assigned by RoutingAgent based on NLP classification",
                    },
                )
            await db.commit()
            await self._update_compliance_scores(db)

        logger.info(f"✅ Routed {len(maps)} MAPs to departments")
        return maps

    async def _update_compliance_scores(self, db):
        """Recalculate compliance score for each department."""
        dept_rows = (await db.execute(text("SELECT name FROM departments"))).fetchall()
        for (dept_name,) in dept_rows:
            total = (await db.execute(
                text("SELECT COUNT(*) FROM maps WHERE department=:d"), {"d": dept_name}
            )).scalar() or 1
            completed = (await db.execute(
                text("SELECT COUNT(*) FROM maps WHERE department=:d AND status='completed'"), {"d": dept_name}
            )).scalar()
            score = round((completed / total) * 100, 1)
            await db.execute(
                text("UPDATE departments SET compliance_score=:score WHERE name=:name"),
                {"score": score, "name": dept_name},
            )
        await db.commit()
        logger.info("✅ Compliance scores updated")
