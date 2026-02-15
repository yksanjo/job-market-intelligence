"""
Job Posting Scraper

Scrapes job postings from company career pages.
"""

import asyncio
import re
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """Job posting data"""
    title: str
    company: str
    location: str = ""
    department: Optional[str] = None
    description: str = ""
    requirements: list[str] = Field(default_factory=list)
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: str = ""  # full-time, part-time, contract
    remote: bool = False
    posted_date: str = ""
    apply_url: str = ""


class JobScraper:
    """Scraper for job postings"""
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def scrape_greenhouse(self, company: str, board_token: str) -> list[JobPosting]:
        """Scrape from Greenhouse board"""
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get("jobs", []):
                jobs.append(JobPosting(
                    title=job.get("title", ""),
                    company=company,
                    location=job.get("location", {}).get("name", ""),
                    department=job.get("department", {}).get("name"),
                    apply_url=job.get("absolute_url", ""),
                    posted_date=job.get("updated_at", "")
                ))
            
            return jobs
        except Exception as e:
            print(f"Error scraping {company}: {e}")
            return []
    
    async def scrape_lever(self, company: str, subdomain: str) -> list[JobPosting]:
        """Scrape from Lever"""
        url = f"https://api.lever.co/v0/postings/{subdomain}"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data:
                # Determine remote
                remote = any(
                    "remote" in job.get("categories", {}).get("location", "").lower(),
                    "remote" in job.get("descriptionPlain", "").lower()
                )
                
                jobs.append(JobPosting(
                    title=job.get("text", ""),
                    company=company,
                    location=job.get("categories", {}).get("location", ""),
                    department=job.get("categories", {}).get("team"),
                    description=job.get("descriptionPlain", ""),
                    remote=remote,
                    apply_url=job.get("applyUrl", "")
                ))
            
            return jobs
        except Exception as e:
            print(f"Error scraping {company}: {e}")
            return []
    
    async def scrape_workday(self, company: str, subdomain: str) -> list[JobPosting]:
        """Scrape from Workday"""
        url = f"https://{subdomain}.workday.com/{subdomain}/jobdings"
        
        jobs = []
        
        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job links
            for link in soup.find_all('a', href=re.compile(r'/job/')):
                title = link.get_text(strip=True)
                if title:
                    jobs.append(JobPosting(
                        title=title,
                        company=company,
                        apply_url=link.get('href', '')
                    ))
        except Exception as e:
            print(f"Error scraping {company}: {e}")
        
        return jobs


# Company examples
COMPANIES = [
    ("Stripe", "greenhouse", "stripe"),
    ("Airbnb", "greenhouse", "airbnb"),
    ("Coinbase", "greenhouse", "coinbase"),
    ("Notion", "lever", "notionhq"),
    ("Figma", "lever", "figma"),
    ("Linear", "lever", "linear"),
    ("Arc", "lever", "arcdotdev"),
]


async def scrape_all_jobs():
    """Scrape jobs from all companies"""
    
    all_jobs = []
    
    async with JobScraper() as scraper:
        for company, platform, token in COMPANIES:
            print(f"Scraping {company} ({platform})...")
            
            if platform == "greenhouse":
                jobs = await scraper.scrape_greenhouse(company, token)
            elif platform == "lever":
                jobs = await scraper.scrape_lever(company, token)
            else:
                jobs = []
            
            print(f"  Found {len(jobs)} jobs")
            all_jobs.extend(jobs)
    
    return all_jobs


if __name__ == "__main__":
    import json
    
    async def main():
        jobs = await scrape_all_jobs()
        
        with open("data/jobs.json", "w") as f:
            json.dump([j.model_dump() for j in jobs], f, indent=2, default=str)
        
        print(f"\nTotal: {len(jobs)} jobs")
    
    asyncio.run(main())
