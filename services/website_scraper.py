import requests
from bs4 import BeautifulSoup
from typing import Dict
import re

class WebsiteScraper:
    def __init__(self):
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'AI', 'ML', 'automation', 'predictive analytics',
            'natural language processing', 'NLP', 'computer vision',
            'data science', 'algorithm', 'model', 'chatbot', 'RPA',
            'digital transformation', 'innovation', 'analytics'
        ]
        
    def analyze_website(self, domain: str) -> Dict:
        """
        Analyze company website for AI/tech mentions
        Returns mock data for demo
        """
        return self._get_mock_website_data(domain)
    
    def _get_mock_website_data(self, domain: str) -> Dict:
        """
        Return mock website analysis data
        """
        mock_data = {
            "goldmansachs.com": {
                "ai_mentions_count": 47,
                "tech_pages": [
                    "/technology/artificial-intelligence",
                    "/careers/engineering",
                    "/about/innovation",
                    "/technology/digital-assets"
                ],
                "key_initiatives": [
                    "AI-powered risk management platform",
                    "Automated trading systems",
                    "Digital client onboarding",
                    "Machine learning for market analysis"
                ],
                "tech_stack_visible": ["Python", "React", "AWS", "Kubernetes"],
                "innovation_score": 82,
                "digital_maturity": "Advanced"
            },
            "jpmorganchase.com": {
                "ai_mentions_count": 68,
                "tech_pages": [
                    "/technology",
                    "/artificial-intelligence",
                    "/innovation",
                    "/digital-banking",
                    "/tech-careers"
                ],
                "key_initiatives": [
                    "COiN - Contract Intelligence platform",
                    "LOXM - AI trading execution",
                    "Fraud detection neural networks",
                    "Customer service chatbots",
                    "Predictive analytics for lending"
                ],
                "tech_stack_visible": ["Python", "Java", "Cloud", "Blockchain"],
                "innovation_score": 91,
                "digital_maturity": "Leading"
            },
            "blackrock.com": {
                "ai_mentions_count": 52,
                "tech_pages": [
                    "/aladdin",
                    "/technology",
                    "/innovation",
                    "/ai-investing"
                ],
                "key_initiatives": [
                    "Aladdin AI enhancement",
                    "Systematic active investing with ML",
                    "Risk analytics automation",
                    "ESG scoring with AI"
                ],
                "tech_stack_visible": ["Python", "Azure", "Scala", "React"],
                "innovation_score": 86,
                "digital_maturity": "Advanced"
            }
        }
        
        # Default data for unknown companies
        default_data = {
            "ai_mentions_count": 3,
            "tech_pages": ["/about", "/products"],
            "key_initiatives": [],
            "tech_stack_visible": ["WordPress"],
            "innovation_score": 25,
            "digital_maturity": "Basic"
        }
        
        # Try to match domain
        for key in mock_data:
            if key in domain or domain in key:
                return mock_data[key]
                
        return default_data
    
    def calculate_tech_presence_score(self, website_data: Dict) -> float:
        """
        Calculate technology presence score based on website analysis
        """
        score = 0
        
        # AI mentions (max 30 points)
        mentions = website_data.get('ai_mentions_count', 0)
        score += min(30, mentions * 0.5)
        
        # Tech pages (max 20 points)
        tech_pages = len(website_data.get('tech_pages', []))
        score += min(20, tech_pages * 5)
        
        # Key initiatives (max 30 points)
        initiatives = len(website_data.get('key_initiatives', []))
        score += min(30, initiatives * 6)
        
        # Tech stack visibility (max 20 points)
        tech_stack = len(website_data.get('tech_stack_visible', []))
        score += min(20, tech_stack * 4)
        
        return min(100, score)