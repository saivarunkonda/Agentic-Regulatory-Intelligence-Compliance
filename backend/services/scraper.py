"""Web scraper service for regulatory portals."""
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict


class RegulationScraper:
    """Scrapes regulatory portals for new updates."""

    async def scrape_rbi(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get("https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx")
                soup = BeautifulSoup(resp.text, "html.parser")
                items = []
                for row in soup.select("table tr")[:10]:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        title = cells[1].get_text(strip=True)
                        link = cells[1].find("a")
                        url = f"https://www.rbi.org.in{link['href']}" if link else ""
                        if title:
                            items.append({"title": title, "url": url, "text": title})
                return items
        except Exception as e:
            logger.warning(f"RBI scrape failed: {e}")
            return []

    async def scrape_sebi(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=3&smid=0"
                )
                soup = BeautifulSoup(resp.text, "html.parser")
                items = []
                for row in soup.select(".mgt15 li")[:10]:
                    title = row.get_text(strip=True)
                    link = row.find("a")
                    url = f"https://www.sebi.gov.in{link['href']}" if link else ""
                    if title:
                        items.append({"title": title[:200], "url": url, "text": title})
                return items
        except Exception as e:
            logger.warning(f"SEBI scrape failed: {e}")
            return []
