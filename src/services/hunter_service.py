"""
Hunter.io API integration service for company and email enrichment
Free tier: 25 searches/month
"""

import os
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class HunterDomainData(BaseModel):
    """Pydantic model for Hunter.io domain search response"""
    
    domain: str
    organization: Optional[str] = None
    
    # Company details
    company_name: Optional[str] = Field(None, alias="organization")
    company_type: Optional[str] = Field(None, alias="type")
    company_size: Optional[str] = Field(None, alias="size")
    company_industry: Optional[str] = Field(None, alias="industry")
    
    # Location
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    
    # Social media
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None
    
    # Technologies detected
    technologies: Optional[List[str]] = Field(default_factory=list)
    
    # Emails found (we'll store a count for privacy)
    email_count: int = 0
    
    # Key people/contacts
    contacts: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class HunterService:
    """
    Service for interacting with Hunter.io API
    Provides company enrichment and email finding capabilities
    """
    
    BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Hunter service
        
        Args:
            api_key: Hunter.io API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("HUNTER_API_KEY")
        if not self.api_key:
            logger.warning("No Hunter.io API key provided. Service will use mock data.")
        
        # Simple in-memory cache (domain -> (data, timestamp))
        self._cache: Dict[str, tuple[Optional[HunterDomainData], datetime]] = {}
        self._cache_ttl_hours = 24
    
    async def search_domain(self, domain: str) -> Optional[HunterDomainData]:
        """
        Search for company information by domain
        
        Args:
            domain: Company domain (e.g., "google.com")
            
        Returns:
            HunterDomainData object or None if not found
        """
        # Normalize domain
        domain = domain.lower().strip()
        if domain.startswith("http://") or domain.startswith("https://"):
            domain = domain.split("//")[1].split("/")[0]
        
        # Check cache first
        cached_data = self._get_from_cache(domain)
        if cached_data is not None:
            logger.info(f"Cache hit for domain: {domain}")
            return cached_data
        
        # If no API key, return mock data for demo
        if not self.api_key:
            return self._get_mock_data(domain)
        
        try:
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/domain-search",
                    params={
                        "domain": domain,
                        "api_key": self.api_key
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    hunter_data = self._parse_hunter_response(data, domain)
                    self._add_to_cache(domain, hunter_data)
                    return hunter_data
                    
                elif response.status_code == 404:
                    logger.info(f"Company not found for domain: {domain}")
                    self._add_to_cache(domain, None)
                    return None
                    
                elif response.status_code == 401:
                    logger.error("Invalid Hunter.io API key")
                    return self._get_mock_data(domain)
                    
                elif response.status_code == 429:
                    logger.error("Hunter.io rate limit exceeded")
                    return self._get_mock_data(domain)
                    
                else:
                    logger.error(f"Hunter.io API error: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching data for domain: {domain}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error fetching Hunter.io data: {e}")
            return None
    
    async def find_contacts(self, domain: str, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find email addresses and contacts for a domain
        
        Args:
            domain: Company domain
            department: Optional department filter (e.g., "executive", "sales", "it")
            
        Returns:
            List of contact dictionaries with name, title, and email pattern
        """
        if not self.api_key:
            return self._get_mock_contacts(domain, department)
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "domain": domain,
                    "api_key": self.api_key
                }
                if department:
                    params["department"] = department
                
                response = await client.get(
                    f"{self.BASE_URL}/email-finder",
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._extract_contacts(data)
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error finding contacts: {e}")
            return []
    
    def _parse_hunter_response(self, data: Dict[str, Any], domain: str) -> HunterDomainData:
        """Parse and validate Hunter.io API response"""
        
        # Hunter.io returns data directly under "data" key
        response_data = data.get("data", {})
        
        # Organization data might be under organization key or directly in data
        if isinstance(response_data, dict):
            org_name = response_data.get("organization")
            emails = response_data.get("emails", [])
        else:
            org_name = None
            emails = []
        
        # If no organization name found, might not have company data
        if not org_name and not emails:
            return None
        
        # Extract key contacts (limit to executives/decision makers)
        contacts = []
        for email_data in emails[:10]:  # Get more contacts for better decision maker identification
            first_name = email_data.get("first_name", "")
            last_name = email_data.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            position = email_data.get("position") or email_data.get("title") or ""
            
            # Include all contacts with emails, even without position
            if email_data.get("value"):  # Has email address
                contacts.append({
                    "first_name": first_name,
                    "last_name": last_name,
                    "name": full_name if full_name else "Unknown",
                    "email": email_data.get("value"),
                    "title": position,
                    "department": email_data.get("department"),
                    "seniority": email_data.get("seniority"),
                    "confidence": email_data.get("confidence", 0),
                    "linkedin": email_data.get("linkedin_url"),
                    "phone": email_data.get("phone_number")
                })
        
        # Build response with available data
        return HunterDomainData(
            domain=domain,
            organization=org_name or domain,
            company_type=None,  # Hunter.io doesn't provide this in basic search
            company_size=None,
            company_industry=None,
            country=response_data.get("country"),
            state=response_data.get("state"),
            city=response_data.get("city"),
            twitter=None,
            facebook=None,
            linkedin=None,
            technologies=[],  # Hunter.io doesn't provide tech stack in domain search
            email_count=len(emails),
            contacts=contacts
        )
    
    def _extract_contacts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract contact information from Hunter.io response"""
        contacts = []
        
        if data.get("data", {}).get("email"):
            # Single email found
            contacts.append({
                "email_pattern": data["data"]["email"],
                "confidence": data["data"].get("score", 0)
            })
        
        # Multiple emails
        for email_data in data.get("data", {}).get("emails", []):
            contacts.append({
                "name": f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                "title": email_data.get("position"),
                "department": email_data.get("department"),
                "confidence": email_data.get("confidence", 0)
            })
        
        return contacts
    
    def _get_from_cache(self, domain: str) -> Optional[HunterDomainData]:
        """Get data from cache if valid"""
        if domain in self._cache:
            data, timestamp = self._cache[domain]
            if datetime.now() - timestamp < timedelta(hours=self._cache_ttl_hours):
                return data
            else:
                del self._cache[domain]
        return None
    
    def _add_to_cache(self, domain: str, data: Optional[HunterDomainData]):
        """Add data to cache"""
        self._cache[domain] = (data, datetime.now())
    
    def _get_mock_data(self, domain: str) -> Optional[HunterDomainData]:
        """Return mock data for testing without API key"""
        mock_companies = {
            "google.com": HunterDomainData(
                domain="google.com",
                organization="Google",
                company_type="Public",
                company_size="10000+",
                company_industry="Internet",
                country="United States",
                state="CA",
                city="Mountain View",
                twitter="google",
                linkedin="google",
                technologies=["Google Analytics", "G Suite", "Google Cloud", "React", "Python"],
                email_count=150,
                contacts=[
                    {"name": "Sundar Pichai", "title": "CEO", "department": "executive", "seniority": "executive"},
                    {"name": "Ruth Porat", "title": "CFO", "department": "finance", "seniority": "executive"}
                ]
            ),
            "modelml.com": HunterDomainData(
                domain="modelml.com",
                organization="ModelML",
                company_type="Private",
                company_size="11-50",
                company_industry="Artificial Intelligence",
                country="United States",
                state="CA",
                city="San Francisco",
                linkedin="modelml",
                technologies=["Python", "TensorFlow", "PyTorch", "AWS", "Docker", "Kubernetes"],
                email_count=12,
                contacts=[
                    {"name": "Alex Chen", "title": "CEO & Founder", "department": "executive", "seniority": "executive"},
                    {"name": "Sarah Johnson", "title": "CTO", "department": "technology", "seniority": "executive"},
                    {"name": "Michael Park", "title": "VP Sales", "department": "sales", "seniority": "senior"}
                ]
            ),
            "stripe.com": HunterDomainData(
                domain="stripe.com",
                organization="Stripe",
                company_type="Private",
                company_size="1000-5000",
                company_industry="Financial Services",
                country="United States",
                state="CA",
                city="San Francisco",
                twitter="stripe",
                linkedin="stripe",
                technologies=["Ruby on Rails", "React", "AWS", "PostgreSQL", "Redis"],
                email_count=85,
                contacts=[
                    {"name": "Patrick Collison", "title": "CEO", "department": "executive", "seniority": "executive"},
                    {"name": "John Collison", "title": "President", "department": "executive", "seniority": "executive"}
                ]
            ),
            "jpmorgan.com": HunterDomainData(
                domain="jpmorgan.com",
                organization="JPMorgan Chase",
                company_type="Public",
                company_size="10000+",
                company_industry="Banking",
                country="United States",
                state="NY",
                city="New York",
                linkedin="jpmorgan",
                technologies=["Java", "Python", "Oracle", "AWS", "Kubernetes"],
                email_count=500,
                contacts=[
                    {"name": "Jamie Dimon", "title": "CEO", "department": "executive", "seniority": "executive"},
                    {"name": "Daniel Pinto", "title": "President & COO", "department": "executive", "seniority": "executive"}
                ]
            ),
            "goldmansachs.com": HunterDomainData(
                domain="goldmansachs.com",
                organization="Goldman Sachs",
                company_type="Public",
                company_size="10000+",
                company_industry="Investment Banking",
                country="United States",
                state="NY",
                city="New York",
                linkedin="goldman-sachs",
                technologies=["Java", "Python", "React", "Slang", "SecDB"],
                email_count=450,
                contacts=[
                    {"name": "David Solomon", "title": "CEO", "department": "executive", "seniority": "executive"},
                    {"name": "John Waldron", "title": "President & COO", "department": "executive", "seniority": "executive"}
                ]
            )
        }
        
        return mock_companies.get(domain)
    
    def _get_mock_contacts(self, domain: str, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return mock contacts for testing"""
        mock_data = self._get_mock_data(domain)
        if mock_data and mock_data.contacts:
            if department:
                return [c for c in mock_data.contacts if c.get("department") == department]
            return mock_data.contacts
        return []
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get Hunter.io account information and remaining searches"""
        if not self.api_key:
            return {"searches_left": "∞ (mock mode)", "plan": "demo"}
        
        try:
            import requests
            response = requests.get(
                f"{self.BASE_URL}/account",
                params={"api_key": self.api_key}
            )
            if response.status_code == 200:
                data = response.json()["data"]
                return {
                    "searches_left": data.get("requests", {}).get("searches", {}).get("available", 0),
                    "plan": data.get("plan_name", "unknown")
                }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
        return None