"""
Clearbit API integration service for company enrichment
"""

import os
import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)


class ClearbitCompanyData(BaseModel):
    """Pydantic model for validated Clearbit company data"""
    
    name: str
    domain: str
    industry: Optional[str] = None
    employee_count: Optional[int] = Field(None, alias="employees")
    employee_range: Optional[str] = Field(None, alias="employeesRange")
    headquarters: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = Field(None, alias="foundedYear")
    
    # Additional useful fields
    tech_stack: Optional[list] = Field(default_factory=list, alias="tech")
    tags: Optional[list] = Field(default_factory=list)
    linkedin_url: Optional[str] = Field(None, alias="linkedin")
    twitter_url: Optional[str] = Field(None, alias="twitter")
    facebook_url: Optional[str] = Field(None, alias="facebook")
    
    # Financial data if available
    funding_total: Optional[float] = Field(None, alias="fundingTotal")
    last_funding_date: Optional[str] = Field(None, alias="lastFundingDate")
    
    class Config:
        populate_by_name = True
    
    @field_validator('employee_count')
    @classmethod
    def validate_employee_count(cls, v):
        if v is not None and v < 0:
            return None
        return v
    
    @field_validator('founded_year')
    @classmethod
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year:
                return None
        return v


class ClearbitAPIError(Exception):
    """Custom exception for Clearbit API errors"""
    pass


class RateLimitExceeded(ClearbitAPIError):
    """Exception raised when rate limit is exceeded"""
    pass


class ClearbitService:
    """
    Service for interacting with Clearbit Company API
    Includes rate limiting, caching, and error handling
    """
    
    BASE_URL = "https://company.clearbit.com/v2/companies"
    MAX_REQUESTS_PER_MINUTE = 600
    CACHE_TTL_HOURS = 24
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Clearbit service
        
        Args:
            api_key: Clearbit API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("CLEARBIT_API_KEY")
        if not self.api_key:
            logger.warning("No Clearbit API key provided. Service will use mock data.")
        
        # Simple in-memory cache (company_domain -> (data, timestamp))
        self._cache: Dict[str, tuple[Optional[ClearbitCompanyData], datetime]] = {}
        
        # Rate limiting tracking
        self._request_timestamps: list[datetime] = []
        self._backoff_until: Optional[datetime] = None
        self._backoff_seconds = 1  # Initial backoff time
        
    async def get_company_data(self, domain: str) -> Optional[ClearbitCompanyData]:
        """
        Fetch company data from Clearbit API or cache
        
        Args:
            domain: Company domain (e.g., "google.com")
            
        Returns:
            ClearbitCompanyData object or None if not found
            
        Raises:
            ClearbitAPIError: For API-related errors
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
        
        # Check rate limiting
        await self._check_rate_limit()
        
        # If no API key, return mock data for demo
        if not self.api_key:
            mock_data = self._get_mock_data(domain)
            self._add_to_cache(domain, mock_data)
            return mock_data
        
        try:
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/find",
                    params={"domain": domain},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )
                
                self._record_request()
                
                if response.status_code == 200:
                    data = response.json()
                    company_data = self._parse_clearbit_response(data)
                    self._add_to_cache(domain, company_data)
                    return company_data
                    
                elif response.status_code == 404:
                    logger.info(f"Company not found for domain: {domain}")
                    self._add_to_cache(domain, None)
                    return None
                    
                elif response.status_code == 429:
                    # Rate limit exceeded
                    await self._handle_rate_limit()
                    raise RateLimitExceeded("Clearbit API rate limit exceeded")
                    
                else:
                    logger.error(f"Clearbit API error: {response.status_code} - {response.text}")
                    raise ClearbitAPIError(f"API returned status {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching data for domain: {domain}")
            return None
            
        except Exception as e:
            if not isinstance(e, (ClearbitAPIError, RateLimitExceeded)):
                logger.error(f"Unexpected error fetching Clearbit data: {e}")
            raise
    
    def _parse_clearbit_response(self, data: Dict[str, Any]) -> ClearbitCompanyData:
        """Parse and validate Clearbit API response"""
        
        # Map Clearbit fields to our model
        mapped_data = {
            "name": data.get("name"),
            "domain": data.get("domain"),
            "industry": data.get("category", {}).get("industry"),
            "employees": data.get("metrics", {}).get("employees"),
            "employeesRange": data.get("metrics", {}).get("employeesRange"),
            "description": data.get("description"),
            "foundedYear": data.get("foundedYear"),
            "tech": data.get("tech", []),
            "tags": data.get("tags", []),
        }
        
        # Location data
        if data.get("location"):
            location = data["location"]
            headquarters = f"{location.get('city', '')}, {location.get('state', '')} {location.get('country', '')}"
            mapped_data["headquarters"] = headquarters.strip()
        
        # Social media links
        if data.get("linkedin"):
            mapped_data["linkedin"] = data["linkedin"].get("handle")
        if data.get("twitter"):
            mapped_data["twitter"] = data["twitter"].get("handle")
        if data.get("facebook"):
            mapped_data["facebook"] = data["facebook"].get("handle")
        
        # Funding data if available
        if data.get("funding"):
            funding = data["funding"]
            mapped_data["fundingTotal"] = funding.get("total")
            if funding.get("lastRound"):
                mapped_data["lastFundingDate"] = funding["lastRound"].get("date")
        
        return ClearbitCompanyData(**mapped_data)
    
    def _get_from_cache(self, domain: str) -> Optional[ClearbitCompanyData]:
        """Get data from cache if valid"""
        if domain in self._cache:
            data, timestamp = self._cache[domain]
            if datetime.now() - timestamp < timedelta(hours=self.CACHE_TTL_HOURS):
                return data
            else:
                # Cache expired
                del self._cache[domain]
        return None
    
    def _add_to_cache(self, domain: str, data: Optional[ClearbitCompanyData]):
        """Add data to cache"""
        self._cache[domain] = (data, datetime.now())
    
    async def _check_rate_limit(self):
        """Check if we're within rate limits"""
        # Check if we're in backoff period
        if self._backoff_until and datetime.now() < self._backoff_until:
            wait_seconds = (self._backoff_until - datetime.now()).total_seconds()
            logger.info(f"Rate limit backoff: waiting {wait_seconds:.1f} seconds")
            await asyncio.sleep(wait_seconds)
        
        # Clean old timestamps (older than 1 minute)
        cutoff = datetime.now() - timedelta(minutes=1)
        self._request_timestamps = [ts for ts in self._request_timestamps if ts > cutoff]
        
        # Check if we're at the limit
        if len(self._request_timestamps) >= self.MAX_REQUESTS_PER_MINUTE:
            # Wait until the oldest request is older than 1 minute
            oldest = self._request_timestamps[0]
            wait_time = 60 - (datetime.now() - oldest).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
    
    def _record_request(self):
        """Record a request timestamp for rate limiting"""
        self._request_timestamps.append(datetime.now())
    
    async def _handle_rate_limit(self):
        """Handle rate limit exceeded with exponential backoff"""
        self._backoff_until = datetime.now() + timedelta(seconds=self._backoff_seconds)
        self._backoff_seconds = min(self._backoff_seconds * 2, 60)  # Max 60 seconds
        logger.warning(f"Rate limit hit, backing off for {self._backoff_seconds} seconds")
    
    def _get_mock_data(self, domain: str) -> Optional[ClearbitCompanyData]:
        """Return mock data for testing without API key"""
        mock_companies = {
            "google.com": ClearbitCompanyData(
                name="Google",
                domain="google.com",
                industry="Technology",
                employees=150000,
                employeesRange="10000+",
                headquarters="Mountain View, CA USA",
                description="Search engine and technology company",
                foundedYear=1998,
                tech=["Google Analytics", "Google Cloud", "TensorFlow"],
                tags=["Technology", "Search", "AI"],
                fundingTotal=25000000
            ),
            "modelml.com": ClearbitCompanyData(
                name="ModelML",
                domain="modelml.com",
                industry="AI/ML Technology",
                employees=50,
                employeesRange="11-50",
                headquarters="San Francisco, CA USA",
                description="AI platform for model deployment and management",
                foundedYear=2021,
                tech=["Python", "TensorFlow", "AWS", "Docker"],
                tags=["AI", "Machine Learning", "MLOps"],
                fundingTotal=10000000
            ),
            "stripe.com": ClearbitCompanyData(
                name="Stripe",
                domain="stripe.com",
                industry="Financial Services",
                employees=7000,
                employeesRange="5000-10000",
                headquarters="San Francisco, CA USA",
                description="Online payment processing for internet businesses",
                foundedYear=2010,
                tech=["Ruby", "React", "AWS"],
                tags=["Fintech", "Payments", "API"],
                fundingTotal=2200000000
            )
        }
        
        return mock_companies.get(domain)
    
    def clear_cache(self):
        """Clear the entire cache"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "entries": len(self._cache),
            "domains": list(self._cache.keys()),
            "oldest_entry": min([ts for _, ts in self._cache.values()], default=None) if self._cache else None
        }