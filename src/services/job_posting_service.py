"""
Job Posting Collection Service using JSearch API
Collects and analyzes job postings to assess AI/ML hiring signals
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import json
import os
from dotenv import load_dotenv

# Load .env from parent directory if it exists there, otherwise current directory
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
logger = logging.getLogger(__name__)


class JobPostingService:
    """
    Service for collecting job posting data via JSearch API (RapidAPI)
    Aggregates data from LinkedIn, Indeed, Glassdoor, ZipRecruiter
    """
    
    BASE_URL = "https://jsearch.p.rapidapi.com"
    MAX_REQUESTS_PER_MINUTE = 100  # RapidAPI tier limit
    CACHE_TTL_HOURS = 24
    
    # Tech roles to search for
    TECH_ROLES = [
        "software engineer",
        "data scientist",
        "machine learning engineer",
        "AI engineer",
        "data engineer",
        "DevOps engineer",
        "ML engineer",
        "artificial intelligence",
        "deep learning engineer",
        "computer vision engineer",
        "NLP engineer",
        # Financial-specific tech roles
        "quantitative analyst",
        "quant developer",
        "quantitative researcher",
        "risk modeler",
        "credit risk analyst",
        "market risk analyst",
        "financial data scientist",
        "financial engineer",
        "algo trader",
        "systematic trader"
    ]
    
    # AI/ML keywords to identify in job descriptions
    AI_ML_KEYWORDS = [
        "tensorflow", "pytorch", "scikit-learn", "keras",
        "machine learning", "deep learning", "artificial intelligence",
        "neural network", "computer vision", "natural language processing",
        "nlp", "data science", "predictive modeling", "reinforcement learning",
        "generative ai", "llm", "large language model", "transformers",
        "hugging face", "opencv", "pandas", "numpy",
        "spark", "hadoop", "databricks", "mlops", "kubeflow",
        "sagemaker", "azure ml", "vertex ai", "ml pipeline",
        # Financial AI/ML keywords
        "quantitative modeling", "risk modeling", "portfolio optimization",
        "algorithmic trading", "backtesting", "monte carlo", "black-scholes",
        "time series", "var", "cvar", "credit scoring", "basel",
        "fraud detection", "anomaly detection", "aml", "kyc", "regulatory reporting"
    ]
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.cache = {}  # Simple in-memory cache
        self.last_request_time = None
        self.request_count = 0
        
        if not self.api_key:
            logger.warning("No RapidAPI key found. Job posting service will use mock data.")
    
    async def search_company_jobs(
        self, 
        company_name: str,
        date_posted: str = "month",  # month, week, today, 3days
        num_pages: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Search for job postings from a specific company
        
        Args:
            company_name: Name of the company to search
            date_posted: Time filter for job postings
            num_pages: Number of pages to retrieve (max 10 per page)
        
        Returns:
            Dictionary with job posting data and analysis
        """
        
        # Check cache first
        cache_key = self._get_cache_key(company_name, date_posted)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"Returning cached job data for {company_name}")
            return cached_result
        
        if not self.api_key:
            logger.info(f"Using mock job data for {company_name}")
            return self._get_mock_data(company_name)
        
        try:
            # Rate limiting
            await self._rate_limit()
            
            # Prepare headers for RapidAPI
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            all_jobs = []
            
            # Search for tech/AI jobs at the company
            if not company_name:
                logger.error("Company name is None or empty")
                return self._get_mock_data("Unknown")
            
            query = f"{company_name} software engineer data scientist machine learning"
            
            async with httpx.AsyncClient(timeout=30) as client:
                for page in range(1, num_pages + 1):
                    params = {
                        "query": query,
                        "date_posted": date_posted,
                        "page": str(page),
                        "num_pages": "1"
                    }
                    
                    response = await client.get(
                        f"{self.BASE_URL}/search",
                        headers=headers,
                        params=params
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "OK" and data.get("data"):
                            all_jobs.extend(data["data"])
                        else:
                            break  # No more results
                    elif response.status_code == 429:
                        logger.warning("Rate limit hit, waiting before retry...")
                        await asyncio.sleep(60)
                    else:
                        logger.error(f"JSearch API error: {response.status_code}")
                        break
            
            # Analyze collected jobs
            result = self._analyze_job_postings(company_name, all_jobs)
            
            # Cache the result
            self._add_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching job postings for {company_name}: {e}")
            return self._get_mock_data(company_name)
    
    def _analyze_job_postings(self, company_name: str, jobs: List[Dict]) -> Dict[str, Any]:
        """
        Analyze job postings for AI/ML signals
        
        Args:
            company_name: Company name
            jobs: List of job postings from JSearch API
        
        Returns:
            Analysis results with AI readiness signals
        """
        
        # Filter for actual company jobs (not just mentions)
        company_jobs = []
        for job in jobs:
            employer = job.get("employer_name", "").lower()
            if company_name.lower() in employer or employer in company_name.lower():
                company_jobs.append(job)
        
        # Categorize jobs
        ai_ml_jobs = []
        tech_jobs = []
        other_jobs = []
        
        for job in company_jobs:
            title = job.get("job_title", "").lower()
            description = job.get("job_description", "").lower()
            
            # Check if it's an AI/ML specific role
            is_ai_ml = False
            for keyword in ["machine learning", "ml engineer", "ai engineer", 
                          "data scientist", "deep learning", "computer vision", "nlp"]:
                if keyword in title or keyword in description[:500]:  # Check title and beginning of description
                    is_ai_ml = True
                    ai_ml_jobs.append(job)
                    break
            
            # If not AI/ML, check if it's a tech role
            if not is_ai_ml:
                for role in ["software", "engineer", "developer", "devops", "data", "cloud"]:
                    if role in title:
                        tech_jobs.append(job)
                        break
                else:
                    other_jobs.append(job)
        
        # Extract AI/ML keywords from all job descriptions
        all_keywords = []
        keyword_counts = {}
        
        for job in company_jobs:
            description = job.get("job_description", "").lower()
            found_keywords = []
            
            for keyword in self.AI_ML_KEYWORDS:
                if keyword in description:
                    found_keywords.append(keyword)
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            if found_keywords:
                all_keywords.extend(found_keywords)
        
        # Calculate signals
        total_jobs = len(company_jobs)
        ai_ml_percentage = (len(ai_ml_jobs) / total_jobs * 100) if total_jobs > 0 else 0
        tech_percentage = (len(tech_jobs) / total_jobs * 100) if total_jobs > 0 else 0
        
        # Top AI/ML technologies mentioned
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Recent job titles (for display)
        recent_job_titles = []
        for job in (ai_ml_jobs + tech_jobs)[:10]:  # Top 10 most relevant
            recent_job_titles.append({
                "title": job.get("job_title"),
                "employer": job.get("employer_name"),
                "location": f"{job.get('job_city') or ''}, {job.get('job_state') or ''}".strip(", "),
                "posted_date": job.get("job_posted_at_datetime_utc"),
                "is_ai_ml": job in ai_ml_jobs
            })
        
        return {
            "company_name": company_name,
            "total_jobs_found": total_jobs,
            "ai_ml_jobs_count": len(ai_ml_jobs),
            "tech_jobs_count": len(tech_jobs),
            "ai_ml_percentage": round(ai_ml_percentage, 1),
            "tech_percentage": round(tech_percentage, 1),
            "top_ai_technologies": [{"keyword": k, "count": v} for k, v in top_keywords],
            "recent_job_titles": recent_job_titles,
            "ai_hiring_intensity": self._calculate_hiring_intensity(len(ai_ml_jobs), total_jobs),
            "tech_stack_signals": list(set(all_keywords))[:20],  # Unique keywords, max 20
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "data_source": "jsearch_api"
        }
    
    def _calculate_hiring_intensity(self, ai_jobs: int, total_jobs: int) -> str:
        """
        Calculate AI hiring intensity level
        
        Args:
            ai_jobs: Number of AI/ML specific jobs
            total_jobs: Total number of jobs
        
        Returns:
            Intensity level: "very_high", "high", "moderate", "low", "none"
        """
        if ai_jobs == 0:
            return "none"
        elif ai_jobs >= 10:
            return "very_high"
        elif ai_jobs >= 5:
            return "high"
        elif ai_jobs >= 2:
            return "moderate"
        else:
            return "low"
    
    async def _rate_limit(self):
        """Implement rate limiting to respect API limits"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < 60:  # Within the same minute
                self.request_count += 1
                if self.request_count >= self.MAX_REQUESTS_PER_MINUTE:
                    wait_time = 60 - elapsed
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)
                    self.request_count = 0
            else:
                self.request_count = 1
        else:
            self.request_count = 1
        
        self.last_request_time = datetime.now()
    
    def _get_cache_key(self, company_name: str, date_posted: str) -> str:
        """Generate cache key for job search"""
        data = f"{company_name}:{date_posted}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if not expired"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=self.CACHE_TTL_HOURS):
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def _add_to_cache(self, cache_key: str, data: Dict):
        """Add data to cache with timestamp"""
        self.cache[cache_key] = (data, datetime.now())
    
    def _get_mock_data(self, company_name: str) -> Dict[str, Any]:
        """
        Return mock job posting data for testing/demo
        
        Args:
            company_name: Company name
        
        Returns:
            Mock job posting analysis
        """
        mock_companies = {
            "google": {
                "total_jobs_found": 42,
                "ai_ml_jobs_count": 18,
                "tech_jobs_count": 20,
                "ai_ml_percentage": 42.9,
                "tech_percentage": 47.6,
                "top_ai_technologies": [
                    {"keyword": "tensorflow", "count": 15},
                    {"keyword": "machine learning", "count": 12},
                    {"keyword": "pytorch", "count": 8},
                    {"keyword": "deep learning", "count": 7},
                    {"keyword": "nlp", "count": 5}
                ],
                "recent_job_titles": [
                    {"title": "Senior ML Engineer", "employer": "Google", "location": "Mountain View, CA", 
                     "posted_date": "2024-01-15", "is_ai_ml": True},
                    {"title": "AI Research Scientist", "employer": "Google", "location": "New York, NY",
                     "posted_date": "2024-01-14", "is_ai_ml": True},
                    {"title": "Data Scientist", "employer": "Google", "location": "Seattle, WA",
                     "posted_date": "2024-01-13", "is_ai_ml": True}
                ],
                "ai_hiring_intensity": "very_high",
                "tech_stack_signals": ["tensorflow", "pytorch", "kubernetes", "cloud", "python"]
            },
            "jpmorgan": {
                "total_jobs_found": 28,
                "ai_ml_jobs_count": 5,
                "tech_jobs_count": 18,
                "ai_ml_percentage": 17.9,
                "tech_percentage": 64.3,
                "top_ai_technologies": [
                    {"keyword": "python", "count": 8},
                    {"keyword": "data science", "count": 4},
                    {"keyword": "machine learning", "count": 3}
                ],
                "recent_job_titles": [
                    {"title": "Quantitative Analyst", "employer": "JPMorgan Chase", "location": "New York, NY",
                     "posted_date": "2024-01-16", "is_ai_ml": False},
                    {"title": "Data Engineer", "employer": "JPMorgan Chase", "location": "Chicago, IL",
                     "posted_date": "2024-01-15", "is_ai_ml": False},
                    {"title": "ML Platform Engineer", "employer": "JPMorgan Chase", "location": "New York, NY",
                     "posted_date": "2024-01-14", "is_ai_ml": True}
                ],
                "ai_hiring_intensity": "moderate",
                "tech_stack_signals": ["python", "sql", "aws", "spark", "java"]
            }
        }
        
        # Default mock data for unknown companies
        default_data = {
            "total_jobs_found": 8,
            "ai_ml_jobs_count": 1,
            "tech_jobs_count": 5,
            "ai_ml_percentage": 12.5,
            "tech_percentage": 62.5,
            "top_ai_technologies": [
                {"keyword": "python", "count": 3},
                {"keyword": "data analysis", "count": 2}
            ],
            "recent_job_titles": [
                {"title": "Software Engineer", "employer": company_name, "location": "Remote",
                 "posted_date": "2024-01-16", "is_ai_ml": False}
            ],
            "ai_hiring_intensity": "low",
            "tech_stack_signals": ["python", "javascript", "sql"]
        }
        
        result = mock_companies.get(company_name.lower(), default_data)
        result["company_name"] = company_name
        result["analysis_timestamp"] = datetime.utcnow().isoformat()
        result["data_source"] = "mock_data"
        
        return result