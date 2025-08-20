"""
BrightData Service for Enhanced Company and LinkedIn Data Collection
Provides real-time LinkedIn profiles, company data, and decision maker identification
"""

import os
import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class BrightDataService:
    """
    Service for collecting enhanced company and LinkedIn data via BrightData
    """
    
    def __init__(self):
        """Initialize BrightData service"""
        self.api_key = os.getenv("BRIGHT_DATA_API")
        self.base_url = "https://api.brightdata.com/datasets/v3"
        
        # Common BrightData dataset IDs
        self.datasets = {
            "linkedin_company": "gd_lflvt8xt520wmz0xk",  # LinkedIn company profiles
            "linkedin_people": "gd_l7q7dkf244hwjntr0",   # LinkedIn people profiles
            "company_info": "gd_lgcd0qf2a0hgb6dqg",      # General company information
        }
        
        if not self.api_key:
            logger.warning("BrightData API key not found. Service will use mock data.")
    
    async def search_linkedin_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for company information on LinkedIn
        
        Args:
            company_name: Name of the company to search
            
        Returns:
            Company profile data from LinkedIn
        """
        if not self.api_key:
            return self._get_mock_linkedin_company(company_name)
        
        try:
            # BrightData Web Scraper API endpoint
            url = "https://api.brightdata.com/request"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Request LinkedIn company data
            payload = {
                "zone": "linkedin_company",
                "url": f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-').replace('.', '')}",
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_linkedin_company(data)
                else:
                    logger.error(f"BrightData API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching LinkedIn company data: {e}")
            return None
    
    async def search_decision_makers(self, company_name: str, titles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for decision makers at a company
        
        Args:
            company_name: Company name
            titles: List of job titles to search for
            
        Returns:
            List of decision maker profiles
        """
        if not self.api_key:
            return self._get_mock_decision_makers(company_name)
        
        if not titles:
            titles = [
                "Chief Technology Officer", "CTO",
                "Chief Data Officer", "CDO",
                "VP Engineering", "VP Data",
                "Director AI", "Director Machine Learning",
                "Head of Data Science", "Head of AI"
            ]
        
        decision_makers = []
        
        try:
            url = "https://api.brightdata.com/request"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Search for each title
            for title in titles[:5]:  # Limit to avoid rate limits
                search_query = f"{title} {company_name}"
                
                payload = {
                    "zone": "linkedin_people_search",
                    "query": search_query,
                    "format": "json"
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        profiles = self._parse_linkedin_profiles(data, company_name)
                        decision_makers.extend(profiles)
                    else:
                        logger.warning(f"Failed to search for {title}: {response.status_code}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
            
            # Deduplicate and sort by relevance
            seen = set()
            unique_dms = []
            for dm in decision_makers:
                key = (dm.get("name"), dm.get("title"))
                if key not in seen:
                    seen.add(key)
                    unique_dms.append(dm)
            
            return unique_dms[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error searching decision makers: {e}")
            return []
    
    async def get_company_insights(self, company_domain: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed company insights
        
        Args:
            company_domain: Company website domain
            
        Returns:
            Detailed company insights
        """
        if not self.api_key:
            return None
        
        try:
            url = "https://api.brightdata.com/request"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "zone": "company_enrichment",
                "domain": company_domain,
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get company insights: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting company insights: {e}")
            return None
    
    def _parse_linkedin_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LinkedIn company data from BrightData response"""
        return {
            "name": data.get("name"),
            "description": data.get("description"),
            "industry": data.get("industry"),
            "size": data.get("company_size"),
            "headquarters": data.get("headquarters"),
            "website": data.get("website"),
            "founded": data.get("founded_year"),
            "specialties": data.get("specialties", []),
            "employee_count": data.get("employee_count"),
            "follower_count": data.get("follower_count"),
            "linkedin_url": data.get("linkedin_url"),
            "recent_updates": data.get("recent_updates", [])
        }
    
    def _parse_linkedin_profiles(self, data: Dict[str, Any], company_name: str) -> List[Dict[str, Any]]:
        """Parse LinkedIn people search results"""
        profiles = []
        
        results = data.get("results", []) if isinstance(data, dict) else []
        
        for profile in results:
            # Filter for current company
            current_company = profile.get("current_company", "").lower()
            if company_name.lower() not in current_company:
                continue
            
            profiles.append({
                "name": profile.get("name"),
                "title": profile.get("title"),
                "company": profile.get("current_company"),
                "location": profile.get("location"),
                "linkedin_url": profile.get("profile_url"),
                "profile_image": profile.get("profile_image"),
                "headline": profile.get("headline"),
                "connections": profile.get("connections"),
                "about": profile.get("about"),
                "experience_years": profile.get("experience_years"),
                "skills": profile.get("skills", [])[:5],
                "education": profile.get("education"),
                "contact_info": profile.get("contact_info", {})
            })
        
        return profiles
    
    def _get_mock_linkedin_company(self, company_name: str) -> Dict[str, Any]:
        """Return mock LinkedIn company data for testing"""
        mock_companies = {
            "jpmorgan": {
                "name": "JPMorgan Chase & Co.",
                "description": "We are a leading global financial services firm with assets of $3.7 trillion.",
                "industry": "Financial Services",
                "size": "10,001+ employees",
                "headquarters": "New York, NY",
                "website": "https://www.jpmorganchase.com",
                "founded": "1799",
                "specialties": ["Investment Banking", "Asset Management", "Commercial Banking", "AI & Machine Learning"],
                "employee_count": 271025,
                "follower_count": 4500000,
                "linkedin_url": "https://www.linkedin.com/company/jpmorganchase/",
                "recent_updates": [
                    "Launched new AI-powered trading platform",
                    "Investing $12B in technology annually",
                    "Hired 3,000+ technologists in 2024"
                ]
            },
            "sequoia": {
                "name": "Sequoia Capital",
                "description": "We help daring founders build legendary companies from idea to IPO and beyond.",
                "industry": "Venture Capital & Private Equity",
                "size": "51-200 employees",
                "headquarters": "Menlo Park, CA",
                "website": "https://www.sequoiacap.com",
                "founded": "1972",
                "specialties": ["Venture Capital", "Growth Investing", "AI/ML Startups", "Technology Investment"],
                "employee_count": 150,
                "follower_count": 850000,
                "linkedin_url": "https://www.linkedin.com/company/sequoia-capital/",
                "recent_updates": [
                    "Led $100M Series B in AI startup",
                    "Launched new AI-focused fund",
                    "Portfolio companies raised $5B in 2024"
                ]
            }
        }
        
        # Find best match
        company_key = company_name.lower().replace(" ", "").replace("&", "").replace(".", "")
        for key in mock_companies:
            if key in company_key:
                return mock_companies[key]
        
        # Default mock data
        return {
            "name": company_name,
            "description": f"Leading company in its industry",
            "industry": "Technology",
            "size": "1,001-5,000 employees",
            "headquarters": "United States",
            "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
            "founded": "2000",
            "specialties": ["Technology", "Innovation"],
            "employee_count": 2500,
            "follower_count": 50000,
            "linkedin_url": f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}/",
            "recent_updates": []
        }
    
    def _get_mock_decision_makers(self, company_name: str) -> List[Dict[str, Any]]:
        """Return mock decision makers for testing"""
        if "jpmorgan" in company_name.lower():
            return [
                {
                    "name": "Lori Beer",
                    "title": "Global Chief Information Officer",
                    "company": "JPMorgan Chase & Co.",
                    "location": "New York, NY",
                    "linkedin_url": "https://www.linkedin.com/in/lori-beer/",
                    "headline": "Global CIO at JPMorgan Chase | Technology Transformation Leader",
                    "skills": ["Digital Transformation", "AI Strategy", "Cloud Computing", "Cybersecurity", "Leadership"],
                    "experience_years": 25
                },
                {
                    "name": "Marco Pistoia",
                    "title": "Managing Director, Head of Applied Research",
                    "company": "JPMorgan Chase & Co.",
                    "location": "New York, NY",
                    "linkedin_url": "https://www.linkedin.com/in/marcopistoia/",
                    "headline": "Head of Applied Research | Quantum Computing & AI Expert",
                    "skills": ["Quantum Computing", "Machine Learning", "Research", "AI", "Financial Technology"],
                    "experience_years": 20
                }
            ]
        elif "sequoia" in company_name.lower():
            return [
                {
                    "name": "Roelof Botha",
                    "title": "Managing Partner",
                    "company": "Sequoia Capital",
                    "location": "San Francisco Bay Area",
                    "linkedin_url": "https://www.linkedin.com/in/roelofbotha/",
                    "headline": "Managing Partner at Sequoia Capital | Investing in the Future",
                    "skills": ["Venture Capital", "Technology Investment", "AI/ML", "Strategic Planning", "Board Leadership"],
                    "experience_years": 20
                },
                {
                    "name": "Konstantine Buhler",
                    "title": "Partner",
                    "company": "Sequoia Capital",
                    "location": "San Francisco Bay Area",
                    "linkedin_url": "https://www.linkedin.com/in/konstantine-buhler/",
                    "headline": "Partner at Sequoia Capital | AI & Crypto Investor",
                    "skills": ["AI Investment", "Cryptocurrency", "Deep Tech", "Venture Capital", "Technology"],
                    "experience_years": 15
                }
            ]
        
        return [
            {
                "name": "[Research needed]",
                "title": "Chief Technology Officer",
                "company": company_name,
                "location": "United States",
                "linkedin_url": "",
                "headline": "Technology Leader",
                "skills": ["Technology Strategy", "Digital Transformation", "AI/ML"],
                "experience_years": 15
            }
        ]