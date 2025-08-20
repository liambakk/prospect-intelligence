"""
News and Press Release Collection Service
For ModelML Prospect Intelligence Tool
"""

import os
import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import json
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsService:
    """
    Service for collecting company news mentions and press releases
    Using NewsAPI.org or alternative sources
    """
    
    def __init__(self):
        """Initialize the news collection service"""
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            "X-Api-Key": self.api_key,
            "User-Agent": "ModelML-Prospect-Intelligence/1.0"
        }
        
        # AI/Tech related keywords for filtering
        self.tech_keywords = [
            "artificial intelligence", "AI", "machine learning", "ML",
            "deep learning", "neural network", "data science",
            "automation", "digital transformation", "technology investment",
            "cloud migration", "big data", "analytics", "predictive",
            "robotics", "computer vision", "NLP", "natural language",
            "tensorflow", "pytorch", "algorithm", "innovation",
            "tech stack", "modernization", "digital strategy"
        ]
        
        # Financial-specific AI keywords
        self.financial_keywords = [
            "regtech", "fintech", "robo-advisor", "algorithmic trading",
            "quantitative analysis", "risk modeling", "fraud detection",
            "compliance automation", "KYC automation", "AML screening",
            "credit scoring", "portfolio optimization", "trade surveillance",
            "regulatory reporting", "Basel III", "MiFID II", "GDPR compliance",
            "real-time payments", "blockchain", "digital banking",
            "open banking", "API banking", "core banking modernization"
        ]
        
        # Preferred financial news sources
        self.financial_sources = [
            "Financial Times", "Wall Street Journal", "Bloomberg",
            "Reuters", "The Banker", "American Banker", "Finextra",
            "Banking Technology", "ThinkAdvisor", "Risk.net",
            "Institutional Investor", "Global Banking & Finance Review"
        ]
        
        # Mock data for testing without API key
        self.use_mock = not bool(self.api_key)
        if self.use_mock:
            logger.warning("NewsAPI key not found. Using mock data for testing.")
    
    async def get_company_news(
        self, 
        company_name: str, 
        days_back: int = 30,
        max_articles: int = 50,
        is_financial: bool = False
    ) -> Dict[str, Any]:
        """
        Search for recent company news mentions with technology focus
        
        Args:
            company_name: Name of the company to search for
            days_back: Number of days to look back for news
            max_articles: Maximum number of articles to return
            
        Returns:
            Dictionary containing news articles and analysis
        """
        if self.use_mock:
            return self._get_mock_news(company_name)
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            # Build search query with company name and relevant keywords
            if is_financial:
                # For financial companies, include fintech and regulatory keywords
                search_query = f'"{company_name}" AND (AI OR "artificial intelligence" OR "machine learning" OR fintech OR regtech OR "risk management" OR "compliance" OR "digital banking" OR "algorithmic trading" OR automation)'
            else:
                search_query = f'"{company_name}" AND (AI OR "artificial intelligence" OR "machine learning" OR "digital transformation" OR technology OR automation)'
            
            async with httpx.AsyncClient() as client:
                # Search everything endpoint for comprehensive results
                response = await client.get(
                    f"{self.base_url}/everything",
                    params={
                        "q": search_query,
                        "from": from_date.strftime("%Y-%m-%d"),
                        "to": to_date.strftime("%Y-%m-%d"),
                        "sortBy": "relevancy",
                        "pageSize": max_articles,
                        "language": "en"
                    },
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Process and analyze articles
                    articles = data.get("articles", [])
                    processed_articles = self._process_articles(company_name, articles, is_financial)
                    
                    return {
                        "total_articles_found": data.get("totalResults", 0),
                        "articles_processed": len(processed_articles),
                        "articles": processed_articles,
                        "ai_mentions_count": self._count_ai_mentions(processed_articles),
                        "tech_focus_score": self._calculate_tech_focus_score(processed_articles),
                        "recent_trends": self._extract_trends(processed_articles),
                        "data_source": "NewsAPI"
                    }
                    
                elif response.status_code == 401:
                    logger.error("Invalid NewsAPI key")
                    return self._get_mock_news(company_name)
                    
                elif response.status_code == 429:
                    logger.error("NewsAPI rate limit exceeded")
                    return {
                        "error": "Rate limit exceeded",
                        "articles": [],
                        "ai_mentions_count": 0
                    }
                    
                else:
                    logger.error(f"NewsAPI error: {response.status_code}")
                    return self._get_mock_news(company_name)
                    
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return self._get_mock_news(company_name)
    
    def _process_articles(self, company_name: str, articles: List[Dict], is_financial: bool = False) -> List[Dict]:
        """
        Process raw articles and extract relevant information
        
        Args:
            company_name: Company name for relevance scoring
            articles: Raw articles from NewsAPI
            
        Returns:
            List of processed articles with metadata
        """
        processed = []
        seen_titles = set()  # For deduplication
        
        for article in articles:
            title = article.get("title", "")
            
            # Skip if duplicate (similar title already seen)
            if self._is_duplicate(title, seen_titles):
                continue
                
            seen_titles.add(title.lower())
            
            # Extract article data
            processed_article = {
                "title": title,
                "description": article.get("description", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "author": article.get("author", "Unknown"),
                "content_snippet": article.get("content", "")[:500] if article.get("content") else "",
                "relevance_score": self._calculate_relevance_score(
                    company_name,
                    title,
                    article.get("description", ""),
                    article.get("content", ""),
                    is_financial
                ),
                "ai_keywords_found": self._extract_ai_keywords(
                    f"{title} {article.get('description', '')} {article.get('content', '')}",
                    is_financial
                )
            }
            
            # Only include articles with reasonable relevance
            if processed_article["relevance_score"] >= 30:
                processed.append(processed_article)
        
        # Sort by relevance score
        processed.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return processed
    
    def _calculate_relevance_score(
        self, 
        company_name: str, 
        title: str, 
        description: str, 
        content: str,
        is_financial: bool = False
    ) -> int:
        """
        Calculate relevance score (0-100) based on keyword density and recency
        
        Args:
            company_name: Company name to check for
            title: Article title
            description: Article description
            content: Article content
            
        Returns:
            Relevance score from 0 to 100
        """
        score = 0
        full_text = f"{title} {description} {content}".lower()
        company_lower = company_name.lower()
        
        # Company name presence (base score)
        if company_lower in title.lower():
            score += 30
        elif company_lower in description.lower():
            score += 20
        elif company_lower in full_text:
            score += 10
        
        # Tech keyword density
        tech_keyword_count = 0
        keywords_to_check = self.tech_keywords
        
        # Add financial keywords if it's a financial company
        if is_financial:
            keywords_to_check = self.tech_keywords + self.financial_keywords
        
        for keyword in keywords_to_check:
            if keyword.lower() in full_text:
                tech_keyword_count += 1
        
        # Add up to 50 points based on keyword density
        keyword_score = min(tech_keyword_count * 5, 50)
        score += keyword_score
        
        # Title relevance boost
        title_boost_keywords = ["ai", "artificial intelligence", "machine learning", "automation"]
        if is_financial:
            title_boost_keywords.extend(["fintech", "regtech", "risk management", "compliance"])
        
        if any(kw in title.lower() for kw in title_boost_keywords):
            score += 20
        
        return min(score, 100)
    
    def _is_duplicate(self, title: str, seen_titles: set) -> bool:
        """
        Check if article is duplicate based on title similarity
        
        Args:
            title: Article title to check
            seen_titles: Set of previously seen titles
            
        Returns:
            True if duplicate, False otherwise
        """
        title_lower = title.lower()
        
        # Check for exact match
        if title_lower in seen_titles:
            return True
        
        # Check for high similarity (simple approach)
        # In production, could use more sophisticated similarity metrics
        title_words = set(title_lower.split())
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            
            # If 80% of words match, consider it duplicate
            if len(title_words) > 3 and len(seen_words) > 3:
                intersection = title_words.intersection(seen_words)
                similarity = len(intersection) / min(len(title_words), len(seen_words))
                if similarity > 0.8:
                    return True
        
        return False
    
    def _extract_ai_keywords(self, text: str, is_financial: bool = False) -> List[str]:
        """
        Extract AI/tech keywords found in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of keywords found
        """
        text_lower = text.lower()
        found_keywords = []
        
        # Check tech keywords
        for keyword in self.tech_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        # Check financial keywords if applicable
        if is_financial:
            for keyword in self.financial_keywords:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
        
        return found_keywords[:10]  # Return top 10 to avoid clutter
    
    def _count_ai_mentions(self, articles: List[Dict]) -> int:
        """
        Count total AI/tech mentions across all articles
        
        Args:
            articles: List of processed articles
            
        Returns:
            Total count of AI mentions
        """
        total_count = 0
        for article in articles:
            total_count += len(article.get("ai_keywords_found", []))
        return total_count
    
    def _calculate_tech_focus_score(self, articles: List[Dict]) -> float:
        """
        Calculate overall technology focus score for the company
        
        Args:
            articles: List of processed articles
            
        Returns:
            Tech focus score (0-100)
        """
        if not articles:
            return 0
        
        # Average relevance score of all articles
        avg_relevance = sum(a["relevance_score"] for a in articles) / len(articles)
        
        # Percentage of articles with high relevance (>60)
        high_relevance_ratio = len([a for a in articles if a["relevance_score"] > 60]) / len(articles)
        
        # Combined score
        tech_focus = (avg_relevance * 0.6) + (high_relevance_ratio * 100 * 0.4)
        
        return round(tech_focus, 1)
    
    def _extract_trends(self, articles: List[Dict]) -> List[str]:
        """
        Extract trending topics from recent articles
        
        Args:
            articles: List of processed articles
            
        Returns:
            List of trending topics/themes
        """
        if not articles:
            return []
        
        # Count keyword frequencies
        keyword_counts = {}
        for article in articles:
            for keyword in article.get("ai_keywords_found", []):
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency and return top trends
        sorted_trends = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [trend[0] for trend in sorted_trends[:5]]
    
    def _get_mock_news(self, company_name: str) -> Dict[str, Any]:
        """
        Return mock news data for testing without API key
        
        Args:
            company_name: Company name for mock data
            
        Returns:
            Mock news data structure
        """
        return {
            "total_articles_found": 15,
            "articles_processed": 5,
            "articles": [
                {
                    "title": f"{company_name} Announces New AI Initiative",
                    "description": f"{company_name} unveils comprehensive artificial intelligence strategy to transform operations",
                    "source": "TechCrunch",
                    "url": "https://example.com/article1",
                    "published_at": datetime.now().isoformat(),
                    "author": "Jane Doe",
                    "content_snippet": "The company announced a major investment in machine learning and automation technologies...",
                    "relevance_score": 85,
                    "ai_keywords_found": ["artificial intelligence", "machine learning", "automation"]
                },
                {
                    "title": f"How {company_name} is Leveraging Machine Learning",
                    "description": "Deep dive into the company's ML infrastructure and capabilities",
                    "source": "VentureBeat",
                    "url": "https://example.com/article2",
                    "published_at": (datetime.now() - timedelta(days=5)).isoformat(),
                    "author": "John Smith",
                    "content_snippet": "Using advanced neural networks and deep learning models...",
                    "relevance_score": 75,
                    "ai_keywords_found": ["machine learning", "deep learning", "neural network"]
                },
                {
                    "title": f"{company_name} Partners on Digital Transformation",
                    "description": "Strategic partnership to accelerate digital initiatives",
                    "source": "Forbes",
                    "url": "https://example.com/article3",
                    "published_at": (datetime.now() - timedelta(days=10)).isoformat(),
                    "author": "Sarah Johnson",
                    "content_snippet": "The digital transformation initiative includes cloud migration and process automation...",
                    "relevance_score": 65,
                    "ai_keywords_found": ["digital transformation", "cloud migration", "automation"]
                }
            ],
            "ai_mentions_count": 8,
            "tech_focus_score": 75.0,
            "recent_trends": ["machine learning", "automation", "digital transformation"],
            "data_source": "Mock Data"
        }


# For testing
async def test_news_service():
    """Test the news service functionality"""
    service = NewsService()
    
    # Test with a known company
    result = await service.get_company_news("Microsoft", days_back=7)
    
    print("News Collection Test Results:")
    print(f"Total articles found: {result.get('total_articles_found', 0)}")
    print(f"Articles processed: {result.get('articles_processed', 0)}")
    print(f"AI mentions count: {result.get('ai_mentions_count', 0)}")
    print(f"Tech focus score: {result.get('tech_focus_score', 0)}")
    print(f"Recent trends: {result.get('recent_trends', [])}")
    
    if result.get("articles"):
        print("\nTop articles:")
        for i, article in enumerate(result["articles"][:3], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Relevance: {article['relevance_score']}")
            print(f"   Keywords: {', '.join(article['ai_keywords_found'][:3])}")
    
    return result


if __name__ == "__main__":
    asyncio.run(test_news_service())