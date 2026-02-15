"""
Greenhouse Job Board Scraper

Scrapes job postings from Greenhouse-hosted career pages.
Many companies use Greenhouse as their ATS (Applicant Tracking System).
"""

import asyncio
import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """A single job posting"""
    job_id: int
    title: str
    company: str
    location: Optional[str] = None
    department: Optional[str] = None
    description: str = ""
    requirements: str = ""
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_url: str
    posted_at: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "department": self.department,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "job_url": self.job_url,
            "posted_at": self.posted_at,
            "scraped_at": self.scraped_at.isoformat()
        }


class GreenhouseScraper:
    """Scraper for Greenhouse job boards"""
    
    BASE_URL = "https://boards-api.greenhouse.io/v1"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=timeout
        )
    
    async def close(self):
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_board_jobs(self, board_token: str) -> list[JobPosting]:
        """
        Get all jobs from a Greenhouse board.
        
        Example: board_token = "airbnb" for airbnb.greenhouse.io
        """
        # Try the JSON API first
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        
        try:
            response = await self.client.get(url, params={"content": "true"})
            if response.status_code == 200:
                return self._parse_json_response(response.json(), board_token)
        except Exception:
            pass
        
        # Fallback to HTML scraping
        return await self._scrape_html_board(board_token)
    
    def _parse_json_response(self, data: dict, company: str) -> list[JobPosting]:
        """Parse JSON response from Greenhouse API"""
        jobs = []
        
        for job in data.get("jobs", []):
            jobs.append(JobPosting(
                job_id=job.get("id", 0),
                title=job.get("title", ""),
                company=company,
                location=job.get("location", {}).get("name"),
                department=job.get("departments", [{}])[0].get("name") if job.get("departments") else None,
                job_url=job.get("absolute_url", ""),
                posted_at=job.get("updated_at")
            ))
        
        return jobs
    
    async def _scrape_html_board(self, board_token: str) -> list[JobPosting]:
        """Fallback: scrape HTML if API fails"""
        url = f"https://{board_token}.greenhouse.io/jobs"
        
        response = await self.client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "lxml")
        jobs = []
        
        # Find job cards
        job_cards = soup.find_all("div", {"class": re.compile(r"job-card")})
        
        for card in job_cards:
            title_elem = card.find("a") or card.find("h2")
            location_elem = card.find("span", {"class": re.compile(r"location")})
            
            if title_elem:
                title = title_elem.get_text().strip()
                url = title_elem.get("href", "")
                if url and not url.startswith("http"):
                    url = f"https://{board_token}.greenhouse.io{url}"
                
                jobs.append(JobPosting(
                    job_id=hash(title),
                    title=title,
                    company=board_token,
                    location=location_elem.get_text().strip() if location_elem else None,
                    job_url=url
                ))
        
        return jobs
    
    async def get_job_details(self, board_token: str, job_id: int) -> JobPosting:
        """Get detailed job posting"""
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}"
        
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract salary if present
        salary_min, salary_max = self._extract_salary(data.get("metadata", []))
        
        return JobPosting(
            job_id=job_id,
            title=data.get("title", ""),
            company=board_token,
            location=data.get("location", {}).get("name"),
            department=data.get("departments", [{}])[0].get("name") if data.get("departments") else None,
            description=data.get("content", ""),
            requirements=data.get("requirements", ""),
            salary_min=salary_min,
            salary_max=salary_max,
            job_url=data.get("absolute_url", ""),
            posted_at=data.get("updated_at")
        )
    
    def _extract_salary(self, metadata: list) -> tuple[Optional[int], Optional[int]]:
        """Extract salary from job metadata"""
        for item in metadata:
            if "salary" in item.get("name", "").lower():
                value = item.get("value", "")
                # Parse salary range like "$150k - $200k"
                numbers = re.findall(r'\d+', value.replace("k", "000").replace("K", "000"))
                if len(numbers) >= 2:
                    return int(numbers[0]), int(numbers[1])
                elif len(numbers) == 1:
                    return int(numbers[0]), int(numbers[0])
        return None, None


# Known Greenhouse boards (common tech companies)
GREENHOUSE_BOARDS = [
    "airbnb", "stripe", "shopify", "notion", "figma",
    "slack", "twilio", "twitch", "coinbase", "discord",
    "robinhood", "dropbox", "zoom", "snowflake", "databricks"
]


async def scrape_company(board_token: str) -> list[JobPosting]:
    """Convenience function to scrape a single company"""
    async with GreenhouseScraper() as scraper:
        return await scraper.get_board_jobs(board_token)


if __name__ == "__main__":
    import json
    import sys
    
    async def main():
        board = sys.argv[1] if len(sys.argv) > 1 else "airbnb"
        
        print(f"Scraping {board}...")
        jobs = await scrape_company(board)
        
        print(f"Found {len(jobs)} jobs:")
        for job in jobs[:10]:
            print(f"  - {job.title} ({job.location})")
        
        # Save
        with open(f"data/{board}_jobs.json", "w") as f:
            json.dump([j.to_dict() for j in jobs], f, indent=2)
    
    asyncio.run(main())
