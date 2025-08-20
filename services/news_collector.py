import requests
from datetime import datetime, timedelta
from typing import Dict, List
import json

class NewsCollector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
        
    def get_recent_news(self, company_name: str) -> Dict:
        """
        Collect recent news about company's AI initiatives
        """
        # For demo, return mock data
        return self._get_mock_news_data(company_name)
    
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