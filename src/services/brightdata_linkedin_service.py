"""
BrightData LinkedIn Scraper Service
Uses BrightData's Web Scraper API for LinkedIn data collection
"""

import os
import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class BrightDataLinkedInService:
    """
    Service for collecting LinkedIn data via BrightData Web Scraper API
    """
    
    def __init__(self):
        """Initialize BrightData service"""
        self.api_key = os.getenv("BRIGHT_DATA_API")
        self.scraper_id = "gd_l1viktl72bvl7bjuj0"  # Your scraper ID
        
        # BrightData API endpoints
        self.base_url = "https://api.brightdata.com"
        self.trigger_url = f"{self.base_url}/dca/trigger"
        self.dataset_url = f"{self.base_url}/dca/dataset"
        
        if not self.api_key:
            logger.warning("BrightData API key not found. Service will use mock data.")
    
    async def scrape_linkedin_profile(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a LinkedIn profile using BrightData
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Profile data
        """
        if not self.api_key:
            return self._get_mock_profile(linkedin_url)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Trigger the scraper
            payload = {
                "collector": self.scraper_id,
                "input": {
                    "url": linkedin_url
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Start the scraping job
                response = await client.post(
                    self.trigger_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    job_data = response.json()
                    job_id = job_data.get("response_id") or job_data.get("job_id")
                    
                    # Wait for results
                    await asyncio.sleep(5)  # Give it time to process
                    
                    # Get the results
                    result_response = await client.get(
                        f"{self.dataset_url}?collector={self.scraper_id}&response_id={job_id}",
                        headers=headers
                    )
                    
                    if result_response.status_code == 200:
                        return self._parse_linkedin_data(result_response.json())
                    else:
                        logger.error(f"Failed to get results: {result_response.status_code}")
                        return None
                else:
                    logger.error(f"Failed to trigger scraper: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error scraping LinkedIn profile: {e}")
            return None
    
    async def search_company_employees(self, company_name: str, titles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for employees at a company
        
        Args:
            company_name: Company name
            titles: List of job titles to search for
            
        Returns:
            List of employee profiles
        """
        if not self.api_key:
            return self._get_mock_employees(company_name)
        
        if not titles:
            titles = [
                "Chief Technology Officer",
                "Chief Data Officer", 
                "VP Engineering",
                "VP Data Science",
                "Director AI",
                "Head of Machine Learning"
            ]
        
        employees = []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            for title in titles[:3]:  # Limit to avoid too many requests
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={title}%20{company_name}"
                
                payload = {
                    "collector": self.scraper_id,
                    "input": {
                        "url": search_url,
                        "search_query": f"{title} {company_name}",
                        "max_results": 5
                    }
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        self.trigger_url,
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        job_data = response.json()
                        job_id = job_data.get("response_id") or job_data.get("job_id")
                        
                        # Wait for results
                        await asyncio.sleep(5)
                        
                        # Get the results
                        result_response = await client.get(
                            f"{self.dataset_url}?collector={self.scraper_id}&response_id={job_id}",
                            headers=headers
                        )
                        
                        if result_response.status_code == 200:
                            profiles = self._parse_search_results(result_response.json(), company_name)
                            employees.extend(profiles)
                    
                # Small delay between searches
                await asyncio.sleep(2)
            
            return employees[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error searching for employees: {e}")
            return self._get_mock_employees(company_name)
    
    async def get_company_page(self, company_linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        Get LinkedIn company page data
        
        Args:
            company_linkedin_url: LinkedIn company page URL
            
        Returns:
            Company data
        """
        if not self.api_key:
            return self._get_mock_company(company_linkedin_url)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "collector": self.scraper_id,
                "input": {
                    "url": company_linkedin_url
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.trigger_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    job_data = response.json()
                    job_id = job_data.get("response_id") or job_data.get("job_id")
                    
                    # Wait for results
                    await asyncio.sleep(5)
                    
                    # Get the results
                    result_response = await client.get(
                        f"{self.dataset_url}?collector={self.scraper_id}&response_id={job_id}",
                        headers=headers
                    )
                    
                    if result_response.status_code == 200:
                        return self._parse_company_data(result_response.json())
                    else:
                        logger.error(f"Failed to get company data: {result_response.status_code}")
                        return None
                else:
                    logger.error(f"Failed to trigger company scraper: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting company page: {e}")
            return None
    
    def _parse_linkedin_data(self, data: Any) -> Dict[str, Any]:
        """Parse LinkedIn profile data from BrightData response"""
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        return {
            "name": data.get("name", ""),
            "title": data.get("title", ""),
            "company": data.get("company", ""),
            "location": data.get("location", ""),
            "about": data.get("about", ""),
            "experience": data.get("experience", []),
            "education": data.get("education", []),
            "skills": data.get("skills", []),
            "linkedin_url": data.get("url", ""),
            "profile_image": data.get("profile_image", ""),
            "connections": data.get("connections", ""),
            "headline": data.get("headline", "")
        }
    
    def _parse_search_results(self, data: Any, company_name: str) -> List[Dict[str, Any]]:
        """Parse search results from BrightData"""
        profiles = []
        
        if isinstance(data, list):
            for item in data:
                # Filter for current company
                if company_name.lower() in item.get("company", "").lower():
                    profiles.append({
                        "name": item.get("name", ""),
                        "title": item.get("title", ""),
                        "company": item.get("company", ""),
                        "location": item.get("location", ""),
                        "linkedin_url": item.get("profile_url", ""),
                        "headline": item.get("headline", ""),
                        "profile_image": item.get("image", "")
                    })
        
        return profiles
    
    def _parse_company_data(self, data: Any) -> Dict[str, Any]:
        """Parse company data from BrightData response"""
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        return {
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "industry": data.get("industry", ""),
            "size": data.get("company_size", ""),
            "headquarters": data.get("headquarters", ""),
            "website": data.get("website", ""),
            "founded": data.get("founded", ""),
            "specialties": data.get("specialties", []),
            "employee_count": data.get("employees_on_linkedin", 0),
            "follower_count": data.get("followers", 0),
            "about": data.get("about", ""),
            "locations": data.get("locations", [])
        }
    
    def _get_mock_profile(self, linkedin_url: str) -> Dict[str, Any]:
        """Return mock profile data for testing"""
        return {
            "name": "John Doe",
            "title": "Chief Technology Officer",
            "company": "Example Corp",
            "location": "San Francisco, CA",
            "about": "Technology leader with 15+ years experience",
            "experience": [],
            "education": [],
            "skills": ["AI", "Machine Learning", "Cloud Computing"],
            "linkedin_url": linkedin_url,
            "headline": "CTO | AI & Digital Transformation Leader"
        }
    
    def _get_mock_employees(self, company_name: str) -> List[Dict[str, Any]]:
        """Return mock employee data for testing"""
        if "jpmorgan" in company_name.lower():
            return [
                {
                    "name": "Lori Beer",
                    "title": "Global Chief Information Officer",
                    "company": "JPMorgan Chase & Co.",
                    "location": "New York, NY",
                    "linkedin_url": "https://www.linkedin.com/in/lori-beer/",
                    "headline": "Global CIO at JPMorgan Chase",
                },
                {
                    "name": "Marco Pistoia",
                    "title": "Managing Director, Head of Applied Research",
                    "company": "JPMorgan Chase & Co.",
                    "location": "New York, NY",
                    "linkedin_url": "https://www.linkedin.com/in/marcopistoia/",
                    "headline": "Head of Applied Research | Quantum Computing & AI",
                }
            ]
        return []
    
    def _get_mock_company(self, company_url: str) -> Dict[str, Any]:
        """Return mock company data for testing"""
        return {
            "name": "Example Company",
            "description": "Leading technology company",
            "industry": "Technology",
            "size": "1000-5000 employees",
            "headquarters": "San Francisco, CA",
            "website": "https://example.com",
            "founded": "2010",
            "specialties": ["AI", "Cloud", "Data"],
            "employee_count": 3000,
            "follower_count": 50000
        }