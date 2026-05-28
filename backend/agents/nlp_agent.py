"""
NLP Agent – Extracts obligations from regulation text and converts to MAPs.
Uses rule-based extraction + optional LLM for richer output.
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict
from database.db import get_db_session
from sqlalchemy import text
from loguru import logger


# ── Keyword maps for obligation and department detection ──────────────────
OBLIGATION_KEYWORDS = [
    "shall", "must", "required", "mandatory", "ensure", "comply",
    "implement", "establish", "maintain", "submit", "report", "review",
    "update", "upgrade", "conduct", "appoint", "file", "notify"
]

DEPARTMENT_KEYWORDS = {
    "Legal": ["legal", "contract", "consent", "officer", "dpo", "data protection", "gdpr", "counsel", "law"],
    "Risk": ["risk", "cdd", "due diligence", "aml", "classification", "assessment", "kyc", "suspicious"],
    "IT": ["system", "it", "technology", "software", "infrastructure", "cyber", "authentication",
           "database", "upgrade", "digital", "ekyc", "aadhaar", "log", "soc", "mfa"],
    "Operations": ["operations", "account", "customer", "record", "transaction", "process", "str",
                   "filing", "report", "branch", "onboard"],
    "Audit": ["audit", "evidence", "tamper", "log", "compliance check", "verify", "review"],
}

PRIORITY_KEYWORDS = {
    "critical": ["immediately", "urgent", "critical", "24 hours", "48 hours", "penalty", "fine"],
    "high":     ["within 30 days", "mandatory", "must", "shall", "june", "march", "deadline"],
    "medium":   ["review", "update", "quarterly", "annually", "implement"],
    "low":      ["consider", "may", "should", "recommend", "optional"],
}


class NLPAgent:
    """Extracts Measurable Action Points from regulatory text."""

    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    def _is_obligation(self, sentence: str) -> bool:
        lower = sentence.lower()
        return any(kw in lower for kw in OBLIGATION_KEYWORDS)

    def _detect_department(self, sentence: str) -> str:
        lower = sentence.lower()
        scores = {dept: 0 for dept in DEPARTMENT_KEYWORDS}
        for dept, keywords in DEPARTMENT_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    scores[dept] += 1
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "Operations"

    def _detect_priority(self, sentence: str) -> str:
        lower = sentence.lower()
        for priority, keywords in PRIORITY_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return priority
        return "medium"

    def _extract_deadline(self, sentence: str) -> str:
        patterns = [
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
            r'\bby\s+(q[1-4]\s+\d{4})\b',
            r'\bwithin\s+(\d+)\s+days\b',
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
            r'\b(\d{4}-\d{2}-\d{2})\b',
        ]
        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                raw = match.group(0)
                if "within" in raw.lower():
                    days = int(re.search(r'\d+', raw).group())
                    return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")
                return raw
        # Default: 90 days from now
        return (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d")

    def _make_title(self, sentence: str) -> str:
        """Generate a short MAP title from an obligation sentence."""
        sentence = re.sub(r'\b(all|the|a|an|its|their|be|are|is|was|were)\b', '', sentence, flags=re.IGNORECASE)
        words = sentence.strip().split()[:10]
        return " ".join(words).strip(" .,;:")

    async def generate_maps(self, regulation_id: int, raw_text: str) -> List[Dict]:
        """Generate MAPs from regulation text and save to DB."""
        sentences = self._split_sentences(raw_text)
        obligation_sentences = [s for s in sentences if self._is_obligation(s)]

        if not obligation_sentences:
            obligation_sentences = sentences[:5]

        maps = []
        async with get_db_session() as db:
            for sentence in obligation_sentences[:8]:  # cap at 8 MAPs per regulation
                department = self._detect_department(sentence)
                priority = self._detect_priority(sentence)
                deadline = self._extract_deadline(sentence)
                title = self._make_title(sentence)
                description = sentence.strip()

                result = await db.execute(
                    text(
                        "INSERT INTO maps (regulation_id, title, description, priority, department, deadline, status, created_at, updated_at) "
                        "VALUES (:rid, :title, :desc, :priority, :dept, :deadline, 'pending', :now, :now) RETURNING id"
                    ),
                    {
                        "rid": regulation_id,
                        "title": title,
                        "desc": description,
                        "priority": priority,
                        "dept": department,
                        "deadline": deadline,
                        "now": datetime.utcnow().isoformat(),
                    },
                )
                map_id = result.scalar()

                # Create alert for critical/high MAPs
                if priority in ("critical", "high"):
                    await db.execute(
                        text("INSERT INTO alerts (map_id, type, message, created_at, resolved) VALUES (:mid, :type, :msg, :now, 0)"),
                        {
                            "mid": map_id,
                            "type": "new_high_priority",
                            "msg": f"New {priority.upper()} MAP assigned to {department}: {title[:60]}",
                            "now": datetime.utcnow().isoformat(),
                        },
                    )

                maps.append({
                    "id": map_id,
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "department": department,
                    "deadline": deadline,
                    "status": "pending",
                })

            # Mark regulation as processed
            await db.execute(
                text("UPDATE regulations SET status='processed' WHERE id=:id"),
                {"id": regulation_id},
            )
            await db.commit()

        logger.info(f"✅ Generated {len(maps)} MAPs for regulation #{regulation_id}")
        return maps
