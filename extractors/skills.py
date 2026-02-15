"""
Skills Extractor

Extracts and normalizes skills from job postings.
"""

import re
from typing import Optional


# Common tech skills database
SKILL_DATABASE = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "go", "rust", "c++", "c#", "ruby",
    "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "shell",
    
    # Frontend
    "react", "vue", "angular", "svelte", "next.js", "nuxt", "gatsby",
    "html", "css", "sass", "tailwind", "bootstrap", "webpack", "vite",
    
    # Backend
    "node.js", "express", "django", "flask", "fastapi", "rails", "spring",
    "graphql", "rest", "grpc", "websocket",
    
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
    "cassandra", "firebase", "supabase", "prisma",
    
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "gitlab ci", "circleci", "cloudformation",
    
    # ML/AI
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "nlp", "computer vision", "pandas", "numpy", "scikit-learn",
    "llm", "gpt", "langchain", "hugging face",
    
    # Data Engineering
    "spark", "hadoop", "kafka", "airflow", "dbt", "etl", "data pipeline",
    
    # Mobile
    "react native", "flutter", "ios", "android", "swiftui", "jetpack compose",
    
    # Other
    "git", "linux", "agile", "scrum", "ci/cd", "rest api", "microservices",
    "system design", "oauth", "jwt", "websocket"
}


class SkillsExtractor:
    """Extract skills from job descriptions"""
    
    def __init__(self):
        self.skill_db = SKILL_DATABASE
    
    def extract_skills(self, text: str) -> list[str]:
        """Extract skills from text"""
        text_lower = text.lower()
        
        found_skills = set()
        
        # Exact matches
        for skill in self.skill_db:
            if skill in text_lower:
                found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name to standard form"""
        skill_lower = skill.lower().strip()
        
        # Normalization mappings
        mappings = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "ts": "typescript",
            "reactjs": "react",
            "react.js": "react",
            "nodejs": "node.js",
            "node": "node.js",
            "postgres": "postgresql",
            "pg": "postgresql",
            "mongo": "mongodb",
            "redis": "redis",
            "aws": "aws",
            "gcp": "gcp",
            "azure": "azure",
            "ml": "machine learning",
            "dl": "deep learning",
            "tf": "tensorflow",
        }
        
        return mappings.get(skill_lower, skill_lower)
    
    def categorize_skills(self, skills: list[str]) -> dict[str, list[str]]:
        """Categorize skills by type"""
        categories = {
            "languages": [],
            "frontend": [],
            "backend": [],
            "databases": [],
            "cloud": [],
            "ml_ai": [],
            "devops": [],
            "other": []
        }
        
        language_skills = {"python", "javascript", "typescript", "java", "go", "rust", 
                         "c++", "c#", "ruby", "php", "swift", "kotlin", "scala"}
        frontend_skills = {"react", "vue", "angular", "svelte", "next.js", "html", "css"}
        backend_skills = {"node.js", "express", "django", "flask", "graphql", "rest"}
        db_skills = {"postgresql", "mysql", "mongodb", "redis", "elasticsearch"}
        cloud_skills = {"aws", "gcp", "azure", "docker", "kubernetes"}
        ml_skills = {"machine learning", "deep learning", "tensorflow", "pytorch", "nlp"}
        
        for skill in skills:
            if skill in language_skills:
                categories["languages"].append(skill)
            elif skill in frontend_skills:
                categories["frontend"].append(skill)
            elif skill in backend_skills:
                categories["backend"].append(skill)
            elif skill in db_skills:
                categories["databases"].append(skill)
            elif skill in cloud_skills:
                categories["cloud"].append(skill)
            elif skill in ml_skills:
                categories["ml_ai"].append(skill)
            else:
                categories["other"].append(skill)
        
        return {k: v for k, v in categories.items() if v}


def extract_from_job(job_text: str) -> dict:
    """Convenience function to extract skills from job posting"""
    extractor = SkillsExtractor()
    skills = extractor.extract_skills(job_text)
    categorized = extractor.categorize_skills(skills)
    
    return {
        "skills": skills,
        "categories": categorized,
        "total_count": len(skills)
    }


if __name__ == "__main__":
    # Test
    test_text = """
    We're looking for a Senior Software Engineer to join our team.
    Requirements:
    - 5+ years experience with Python, JavaScript, TypeScript
    - Experience with React, Django, PostgreSQL
    - Familiarity with AWS, Docker, Kubernetes
    - Nice to have: Machine Learning, TensorFlow
    """
    
    result = extract_from_job(test_text)
    print(f"Found {result['total_count']} skills:")
    print(f"  Skills: {result['skills']}")
    print(f"  Categorized: {result['categories']}")
