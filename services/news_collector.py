import requests
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os

class NewsCollector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('NEWS_API_KEY', '0e6445a05ca1433787be3ea4b5e03bc7')
        self.base_url = "https://newsapi.org/v2/everything"
        
    def get_recent_news(self, company_name: str) -> Dict:
        """
        Collect recent news about company's AI initiatives
        """
        # Try to get real news data first
        if self.api_key:
            try:
                real_data = self._fetch_real_news(company_name)
                if real_data:
                    return real_data
            except Exception as e:
                print(f"Error fetching news: {e}")
        
        # Fallback to mock data
        return self._get_mock_news_data(company_name)
    
    def _fetch_real_news(self, company_name: str) -> Dict:
        """
        Fetch real news from News API
        """
        # Calculate date range (last 30 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        # Search for company + AI/tech keywords
        ai_keywords = ['AI', 'artificial intelligence', 'machine learning', 'automation', 'digital transformation']
        
        all_articles = []
        ai_articles = []
        
        # First, get general company news
        params = {
            'q': f'"{company_name}"',
            'apiKey': self.api_key,
            'from': from_date.isoformat(),
            'to': to_date.isoformat(),
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': 20
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                all_articles = data.get('articles', [])
            else:
                print(f"News API error: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching general news: {e}")
        
        # Now search for AI-specific news
        for keyword in ai_keywords[:3]:  # Limit to avoid rate limits
            params['q'] = f'"{company_name}" AND ({keyword})'
            
            try:
                response = requests.get(self.base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        # Check if article is actually about AI
                        title = article.get('title', '').lower()
                        description = article.get('description', '').lower()
                        content = article.get('content', '').lower()
                        
                        if any(kw.lower() in title + description + content for kw in ai_keywords):
                            ai_articles.append(article)
                            
            except Exception as e:
                print(f"Error fetching AI news for keyword {keyword}: {e}")
        
        # Process and format the articles
        recent_initiatives = []
        ai_mentions_count = 0
        
        # Deduplicate AI articles by URL
        seen_urls = set()
        unique_ai_articles = []
        for article in ai_articles:
            url = article.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_ai_articles.append(article)
        
        # Process top AI articles
        for article in unique_ai_articles[:5]:
            title = article.get('title', '')
            description = article.get('description', '')
            
            # Count AI mentions
            content_text = (title + ' ' + description).lower()
            ai_mentions_count += sum(1 for kw in ai_keywords if kw.lower() in content_text)
            
            # Determine sentiment
            sentiment = self._analyze_sentiment_simple(title, description)
            
            recent_initiatives.append({
                'title': title[:100],  # Truncate long titles
                'date': article.get('publishedAt', '')[:10],  # Just date part
                'source': article.get('source', {}).get('name', 'Unknown'),
                'summary': description[:200] if description else 'No summary available',
                'sentiment': sentiment,
                'url': article.get('url', '')
            })
        
        # Calculate digital transformation score
        transformation_score = min(100, len(unique_ai_articles) * 10 + ai_mentions_count * 2)
        
        result = {
            'total_articles': len(all_articles),
            'ai_related_articles': len(unique_ai_articles),
            'recent_initiatives': recent_initiatives,
            'ai_mentions_frequency': ai_mentions_count,
            'digital_transformation_score': transformation_score
        }
        
        return result
    
    def _analyze_sentiment_simple(self, title: str, description: str) -> str:
        """
        Simple sentiment analysis based on keywords
        """
        text = (title + ' ' + description).lower()
        
        positive_words = ['success', 'growth', 'innovation', 'leading', 'breakthrough', 
                         'advanced', 'pioneer', 'transform', 'excel', 'improve']
        negative_words = ['challenge', 'risk', 'concern', 'struggle', 'decline', 
                         'threat', 'problem', 'issue', 'difficult', 'fail']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count + 2:
            return "very positive"
        elif positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _get_mock_news_data(self, company_name: str) -> Dict:
        """
        Return mock news data for demonstration
        """
        mock_news = {
            "Goldman Sachs": {
                "total_articles": 12,
                "ai_related_articles": 8,
                "recent_initiatives": [
                    {
                        "title": "Goldman Sachs Launches AI-Powered Trading Platform",
                        "date": "2024-01-15",
                        "source": "Financial Times",
                        "summary": "Investment bank deploys machine learning for automated trading decisions",
                        "sentiment": "positive"
                    },
                    {
                        "title": "Goldman Partners with AI Startup for Risk Management",
                        "date": "2024-01-10",
                        "source": "Bloomberg",
                        "summary": "Strategic partnership to enhance risk analytics using deep learning",
                        "sentiment": "positive"
                    },
                    {
                        "title": "Goldman Sachs Invests $100M in AI Research Lab",
                        "date": "2023-12-20",
                        "source": "Wall Street Journal",
                        "summary": "New lab to focus on generative AI for financial services",
                        "sentiment": "very positive"
                    }
                ],
                "ai_mentions_frequency": 67,
                "digital_transformation_score": 85
            },
            "JPMorgan Chase": {
                "total_articles": 18,
                "ai_related_articles": 14,
                "recent_initiatives": [
                    {
                        "title": "JPMorgan Deploys AI Across 300,000 Employees",
                        "date": "2024-01-18",
                        "source": "Reuters",
                        "summary": "Bank rolls out AI assistants for productivity and analysis",
                        "sentiment": "very positive"
                    },
                    {
                        "title": "JPMorgan's AI Chief: 'We're Just Getting Started'",
                        "date": "2024-01-12",
                        "source": "CNBC",
                        "summary": "Interview reveals ambitious AI roadmap for next 5 years",
                        "sentiment": "positive"
                    },
                    {
                        "title": "JPMorgan Files Patent for AI-Based Fraud Detection",
                        "date": "2024-01-08",
                        "source": "TechCrunch",
                        "summary": "New system uses neural networks to detect fraudulent transactions",
                        "sentiment": "positive"
                    },
                    {
                        "title": "JPMorgan Leads $50M Investment in AI Fintech",
                        "date": "2023-12-28",
                        "source": "Forbes",
                        "summary": "Strategic investment in AI-powered financial planning platform",
                        "sentiment": "positive"
                    }
                ],
                "ai_mentions_frequency": 89,
                "digital_transformation_score": 92
            },
            "BlackRock": {
                "total_articles": 9,
                "ai_related_articles": 7,
                "recent_initiatives": [
                    {
                        "title": "BlackRock's Aladdin Platform Adds Generative AI Features",
                        "date": "2024-01-14",
                        "source": "Financial Times",
                        "summary": "AI enhancements to help portfolio managers with analysis",
                        "sentiment": "positive"
                    },
                    {
                        "title": "BlackRock CEO: AI Will Transform Asset Management",
                        "date": "2024-01-05",
                        "source": "Bloomberg",
                        "summary": "Larry Fink outlines vision for AI-driven investment strategies",
                        "sentiment": "positive"
                    },
                    {
                        "title": "BlackRock Acquires AI Analytics Startup",
                        "date": "2023-12-15",
                        "source": "Wall Street Journal",
                        "summary": "Acquisition strengthens AI capabilities for risk assessment",
                        "sentiment": "very positive"
                    }
                ],
                "ai_mentions_frequency": 78,
                "digital_transformation_score": 88
            }
        }
        
        # Default data for unknown companies
        default_data = {
            "total_articles": 3,
            "ai_related_articles": 0,
            "recent_initiatives": [],
            "ai_mentions_frequency": 5,
            "digital_transformation_score": 30
        }
        
        # Try to match company name
        for key in mock_news:
            if key.lower() in company_name.lower() or company_name.lower() in key.lower():
                return mock_news[key]
                
        return default_data
    
    def analyze_sentiment(self, articles: List[Dict]) -> str:
        """
        Analyze overall sentiment from news articles
        """
        if not articles:
            return "neutral"
            
        sentiment_scores = {
            "very positive": 2,
            "positive": 1,
            "neutral": 0,
            "negative": -1,
            "very negative": -2
        }
        
        total_score = sum(sentiment_scores.get(article.get('sentiment', 'neutral'), 0) 
                         for article in articles)
        avg_score = total_score / len(articles)
        
        if avg_score >= 1.5:
            return "very positive"
        elif avg_score >= 0.5:
            return "positive"
        elif avg_score >= -0.5:
            return "neutral"
        elif avg_score >= -1.5:
            return "negative"
        else:
            return "very negative"