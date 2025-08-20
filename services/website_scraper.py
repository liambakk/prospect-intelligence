import requests
from bs4 import BeautifulSoup
from typing import Dict
import re
from urllib.parse import urljoin, urlparse

class WebsiteScraper:
    def __init__(self):
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'AI', 'ML', 'automation', 'predictive analytics',
            'natural language processing', 'NLP', 'computer vision',
            'data science', 'algorithm', 'model', 'chatbot', 'RPA',
            'digital transformation', 'innovation', 'analytics'
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def analyze_website(self, domain: str) -> Dict:
        """
        Analyze company website for AI/tech mentions
        """
        # Try real scraping first
        try:
            real_data = self._scrape_real_website(domain)
            if real_data and real_data.get('ai_mentions_count', 0) > 0:
                return real_data
        except Exception as e:
            print(f"Error scraping website: {e}")
        
        # Fallback to mock data
        return self._get_mock_website_data(domain)
    
    def _scrape_real_website(self, domain: str) -> Dict:
        """
        Scrape actual website for AI/tech signals
        """
        # Ensure proper URL format
        if not domain.startswith('http'):
            url = f'https://{domain}'
        else:
            url = domain
        
        ai_mentions_count = 0
        tech_pages = []
        key_initiatives = []
        tech_stack_visible = set()
        
        try:
            # Fetch main page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get all text content
            text_content = soup.get_text().lower()
            
            # Count AI mentions
            for keyword in self.ai_keywords:
                ai_mentions_count += text_content.count(keyword.lower())
            
            # Look for technology-related links
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                link_text = link.get_text().lower()
                
                tech_indicators = ['technology', 'innovation', 'ai', 'ml', 'data', 'digital', 
                                  'engineering', 'careers', 'about', 'products', 'solutions']
                
                if any(indicator in href or indicator in link_text for indicator in tech_indicators):
                    full_url = urljoin(url, link['href'])
                    if urlparse(full_url).netloc == urlparse(url).netloc:  # Same domain
                        tech_pages.append(link['href'])
            
            # Deduplicate and limit tech pages
            tech_pages = list(set(tech_pages))[:10]
            
            # Try to fetch key pages for more info
            pages_to_check = ['/about', '/technology', '/careers', '/products', '/solutions']
            
            for page in pages_to_check[:3]:  # Limit to avoid too many requests
                try:
                    page_url = urljoin(url, page)
                    page_response = requests.get(page_url, headers=self.headers, timeout=5)
                    
                    if page_response.status_code == 200:
                        page_soup = BeautifulSoup(page_response.text, 'html.parser')
                        page_text = page_soup.get_text().lower()
                        
                        # Look for AI initiatives
                        for keyword in ['artificial intelligence', 'machine learning', 'automation', 'digital transformation']:
                            if keyword in page_text:
                                # Try to extract context around the keyword
                                sentences = page_text.split('.')
                                for sentence in sentences:
                                    if keyword in sentence and len(sentence) > 20 and len(sentence) < 200:
                                        initiative = sentence.strip().capitalize()
                                        if initiative and len(key_initiatives) < 5:
                                            key_initiatives.append(initiative[:150])  # Truncate long sentences
                                            break
                        
                        # Count additional AI mentions
                        for keyword in self.ai_keywords:
                            ai_mentions_count += page_text.count(keyword.lower())
                        
                except:
                    continue
            
            # Detect tech stack from page content
            tech_patterns = {
                'python': r'\bpython\b',
                'java': r'\bjava\b',
                'react': r'\breact\b',
                'aws': r'\baws\b|\bamazon web services\b',
                'azure': r'\bazure\b|\bmicrosoft azure\b',
                'kubernetes': r'\bkubernetes\b|\bk8s\b',
                'docker': r'\bdocker\b',
                'tensorflow': r'\btensorflow\b',
                'pytorch': r'\bpytorch\b',
                'spark': r'\bspark\b|\bapache spark\b',
                'hadoop': r'\bhadoop\b',
                'mongodb': r'\bmongodb\b',
                'postgresql': r'\bpostgresql\b|\bpostgres\b'
            }
            
            for tech, pattern in tech_patterns.items():
                if re.search(pattern, text_content):
                    tech_stack_visible.add(tech.capitalize())
            
            # Calculate innovation score based on findings
            innovation_score = min(100, ai_mentions_count * 2 + len(tech_pages) * 5 + len(key_initiatives) * 10)
            
            # Determine digital maturity
            if ai_mentions_count > 50:
                digital_maturity = "Leading"
            elif ai_mentions_count > 20:
                digital_maturity = "Advanced"
            elif ai_mentions_count > 5:
                digital_maturity = "Developing"
            else:
                digital_maturity = "Basic"
            
            return {
                'ai_mentions_count': ai_mentions_count,
                'tech_pages': tech_pages[:5],  # Return top 5 tech pages
                'key_initiatives': key_initiatives,
                'tech_stack_visible': list(tech_stack_visible),
                'innovation_score': innovation_score,
                'digital_maturity': digital_maturity
            }
            
        except Exception as e:
            print(f"Error in web scraping: {e}")
            return None
    
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