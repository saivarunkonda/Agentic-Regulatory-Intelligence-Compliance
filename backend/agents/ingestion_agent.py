"""
Ingestion Agent – Scrapes regulatory feeds and stores regulations in DB.
"""
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import fitz  # PyMuPDF
from database.db import get_db_session
from sqlalchemy import text
from loguru import logger


REGULATORY_SOURCES = [
    {
        "name": "RBI",
        "url": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
        "type": "html",
    },
    {
        "name": "SEBI",
        "url": "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=3&smid=0",
        "type": "html",
    },
]


class IngestionAgent:
    """Monitors and ingests regulatory changes from multiple sources."""

    async def run_ingestion_cycle(self):
        """Full ingestion cycle – fetch from all sources."""
        logger.info("🔄 Starting ingestion cycle...")
        ingested = 0
        for source in REGULATORY_SOURCES:
            try:
                items = await self._fetch_source(source)
                for item in items:
                    await self.ingest_text(item["title"], source["name"], item["text"], item.get("url"))
                    ingested += 1
            except Exception as e:
                logger.error(f"❌ Failed to ingest from {source['name']}: {e}")
        logger.info(f"✅ Ingestion complete – {ingested} items")
        return ingested

    async def _fetch_source(self, source: dict) -> list:
        """Fetch regulatory updates from a source (mock for hackathon)."""
        # For demo: return mock items since actual scraping may be blocked
        return []

    async def ingest_text(self, title: str, source: str, raw_text: str, url: str = None) -> int:
        """Ingest raw text regulation into DB."""
        async with get_db_session() as db:
            result = await db.execute(
                text(
                    "INSERT INTO regulations (title, source, url, raw_text, status, created_at) "
                    "VALUES (:title, :source, :url, :raw_text, 'new', :now) RETURNING id"
                ),
                {
                    "title": title,
                    "source": source,
                    "url": url or "",
                    "raw_text": raw_text,
                    "now": datetime.utcnow().isoformat(),
                },
            )
            reg_id = result.scalar()
            await db.commit()
            logger.info(f"✅ Ingested regulation #{reg_id}: {title}")
            return reg_id

    async def ingest_pdf(self, filename: str, content: bytes) -> int:
        """Parse PDF and ingest as regulation."""
        doc = fitz.open(stream=content, filetype="pdf")
        text_content = ""
        for page in doc:
            text_content += page.get_text()
        doc.close()
        title = filename.replace(".pdf", "").replace("_", " ").title()
        return await self.ingest_text(title, "PDF Upload", text_content[:5000])
