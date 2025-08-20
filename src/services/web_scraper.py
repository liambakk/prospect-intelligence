"""
Web scraping service for extracting technology signals from company websites
"""

import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import re
import logging

logger = logging.getLogger(__name__)


class WebScraperService:
    """
    Service for scraping company websites to extract technology signals
    """
    
    # AI/ML related keywords to search for
    AI_KEYWORDS = [
        "artificial intelligence", "machine learning", "deep learning",
        "neural network", "data science", "ai-powered", "ml model",
        "predictive analytics", "computer vision", "natural language processing",
        "nlp", "automation", "intelligent", "algorithm", "tensorflow",
        "pytorch", "scikit-learn", "data pipeline", "mlops", "ai platform",
        # Financial AI keywords
        "robo-advisor", "algorithmic trading", "fraud detection",
        "credit scoring", "risk modeling", "regtech", "fintech",
        "quantitative analysis", "aml screening", "kyc automation",
        "trade surveillance", "market surveillance", "compliance automation"
    ]
    
    # Technology stack indicators
    TECH_INDICATORS = {
        "cloud": ["aws", "azure", "gcp", "google cloud", "cloud-native", "kubernetes", "docker"],
        "modern_stack": ["react", "vue", "angular", "node.js", "python", "golang", "rust"],
        "data": ["spark", "hadoop", "kafka", "elasticsearch", "mongodb", "postgresql", 
                 "snowflake", "databricks", "palantir", "alteryx"],
        "ai_tools": ["tensorflow", "pytorch", "hugging face", "openai", "langchain", "jupyter"],
        "financial_systems": ["bloomberg", "refinitiv", "factset", "murex", "calypso",
                             "fidessa", "temenos", "finastra", "fis", "fiserv"],
        "compliance_tools": ["actimize", "verafin", "fenergo", "accuity", "lexisnexis"]
    }
    
    def __init__(self):
        self.session_timeout = 10.0
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
    
    async def scrape_company_website(self, domain: str) -> Dict[str, Any]:
        """
        Scrape a company website for technology signals
        
        Args:
            domain: Company domain (e.g., "example.com")
            
        Returns:
            Dictionary with extracted signals
        """
        # Ensure proper URL format
        if not domain.startswith("http"):
            url = f"https://{domain}"
        else:
            url = domain
        
        try:
            # Fetch main page
            main_page_data = await self._fetch_page(url)
            if not main_page_data:
                return self._empty_result()
            
            # Extract signals from main page
            ai_mentions = self._count_ai_mentions(main_page_data['text'])
            tech_stack = self._detect_tech_stack(main_page_data['text'])
            
            # Try to find and scrape specific pages
            careers_url = self._find_careers_url(main_page_data['html'], url)
            about_url = self._find_about_url(main_page_data['html'], url)
            
            careers_signals = {}
            about_signals = {}
            
            if careers_url:
                careers_data = await self._fetch_page(careers_url)
                if careers_data:
                    careers_signals = {
                        'ai_roles': self._detect_ai_roles(careers_data['text']),
                        'tech_roles_count': self._count_tech_roles(careers_data['text'])
                    }
            
            if about_url:
                about_data = await self._fetch_page(about_url)
                if about_data:
                    about_signals = {
                        'mission_ai_mentions': self._count_ai_mentions(about_data['text'])
                    }
            
            return {
                "domain": domain,
                "ai_mentions_count": ai_mentions,
                "tech_stack_detected": tech_stack,
                "careers_signals": careers_signals,
                "about_signals": about_signals,
                "ai_readiness_signals": self._calculate_signals_score(
                    ai_mentions, tech_stack, careers_signals
                )
            }
            
        except Exception as e:
            logger.error(f"Error scraping {domain}: {e}")
            return self._empty_result()
    
    async def _fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and parse a web page"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": self.user_agents[0],
                        "Accept": "text/html,application/xhtml+xml"
                    },
                    timeout=self.session_timeout,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text = soup.get_text()
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    return {
                        "html": response.text,
                        "text": text.lower(),
                        "soup": soup
                    }
                    
        except Exception as e:
            logger.debug(f"Could not fetch {url}: {e}")
        
        return None
    
    def _count_ai_mentions(self, text: str) -> int:
        """Count AI-related keyword mentions"""
        count = 0
        for keyword in self.AI_KEYWORDS:
            count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
        return count
    
    def _detect_tech_stack(self, text: str) -> List[str]:
        """Detect technology stack from text"""
        detected = []
        for category, keywords in self.TECH_INDICATORS.items():
            for keyword in keywords:
                if keyword in text:
                    detected.append(keyword)
        return list(set(detected))  # Remove duplicates
    
    def _detect_ai_roles(self, text: str) -> List[str]:
        """Detect AI-related job roles"""
        ai_roles = [
            "machine learning engineer", "ml engineer", "data scientist",
            "ai engineer", "ai researcher", "deep learning engineer",
            "computer vision engineer", "nlp engineer", "mlops engineer"
        ]
        
        found_roles = []
        for role in ai_roles:
            if role in text:
                found_roles.append(role)
        
        return found_roles
    
    def _count_tech_roles(self, text: str) -> int:
        """Count technology job openings"""
        tech_keywords = ["engineer", "developer", "architect", "devops", "data"]
        count = 0
        for keyword in tech_keywords:
            count += text.count(keyword)
        return min(count, 50)  # Cap at 50 to avoid inflation
    
    def _find_careers_url(self, html: str, base_url: str) -> Optional[str]:
        """Find careers/jobs page URL"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for careers/jobs links
        patterns = ["careers", "jobs", "join", "hiring", "work-with-us"]
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().lower()
            
            for pattern in patterns:
                if pattern in href or pattern in text:
                    return urljoin(base_url, link['href'])
        
        # Try common URLs
        domain = urlparse(base_url).netloc
        for pattern in ["careers", "jobs"]:
            test_url = f"https://{domain}/{pattern}"
            return test_url  # Return first common pattern to try
        
        return None
    
    def _find_about_url(self, html: str, base_url: str) -> Optional[str]:
        """Find about page URL"""
        soup = BeautifulSoup(html, 'html.parser')
        
        patterns = ["about", "about-us", "company", "who-we-are"]
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().lower()
            
            for pattern in patterns:
                if pattern in href or pattern in text:
                    return urljoin(base_url, link['href'])
        
        return None
    
    def _calculate_signals_score(
        self, 
        ai_mentions: int, 
        tech_stack: List[str], 
        careers_signals: Dict
    ) -> Dict[str, Any]:
        """Calculate AI readiness signals score"""
        
        score = 0
        signals = []
        
        # AI mentions scoring
        if ai_mentions > 20:
            score += 30
            signals.append("Strong AI focus")
        elif ai_mentions > 10:
            score += 20
            signals.append("Moderate AI mentions")
        elif ai_mentions > 5:
            score += 10
            signals.append("Some AI mentions")
        
        # Tech stack scoring
        if len(tech_stack) > 10:
            score += 25
            signals.append("Modern tech stack")
        elif len(tech_stack) > 5:
            score += 15
            signals.append("Good tech adoption")
        elif len(tech_stack) > 0:
            score += 5
            signals.append("Basic tech presence")
        
        # Careers signals scoring
        if careers_signals:
            if careers_signals.get('ai_roles'):
                score += 20
                signals.append(f"Hiring for AI roles")
            if careers_signals.get('tech_roles_count', 0) > 10:
                score += 10
                signals.append("Active tech hiring")
        
        return {
            "score": min(score, 100),
            "signals": signals,
            "confidence": 0.6 if score > 0 else 0.3
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "domain": "",
            "ai_mentions_count": 0,
            "tech_stack_detected": [],
            "careers_signals": {},
            "about_signals": {},
            "ai_readiness_signals": {
                "score": 0,
                "signals": [],
                "confidence": 0.1
            }
        }