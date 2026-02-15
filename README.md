# Global Job Market Intelligence

Track job postings, extract skills, and analyze hiring trends across the web.

## Why This Exists

Understanding the job market is crucial for:
- Job seekers: Know what skills are in demand
- Recruiters: Understand salary ranges and skill requirements  
- Investors: Track company hiring velocity
- Founders: Make data-driven hiring decisions

## Features

- 🔍 Scrape job postings from multiple sources
- 🏢 Track company hiring signals
- 💰 Extract salary data
- 🛠️ Extract and normalize skills
- 📈 Analyze trends over time
- 🎯 Identify emerging roles

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Scrape a job board
python main.py scrape --source greenhouse

# Analyze skills in job postings
python -c "from analyzer import SkillsAnalyzer; print(SkillsAnalyzer().extract_skills('Python, React, AWS'))"
```

## Data Sources

- Greenhouse (ATS)
- Lever (ATS)
- Company career pages
- Job boards (optional)

## Project Structure

```
job-market-intelligence/
├── scrapers/       # Job posting scrapers
├── extractors/     # Skill & salary extraction
├── analyzer/       # Trend analysis
├── data/          # Stored data
└── main.py        # CLI entry point
```

## License

MIT
