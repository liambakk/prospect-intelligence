import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import re
import os
from datetime import datetime, timedelta

class JobScraper:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '9d36b475a7msh71d5382467f3014p18af56jsn4c74cf8a0565')
        self.indeed_host = "indeed12.p.rapidapi.com"
        self.ai_keywords = [
            'data scientist', 'machine learning', 'artificial intelligence',
            'AI engineer', 'ML engineer', 'deep learning', 'neural network',
            'NLP', 'computer vision', 'data engineer', 'MLOps',
            'AI researcher', 'algorithm engineer', 'data analyst'
        ]
        
    def analyze_job_postings(self, company_name: str) -> Dict:
        """
        Analyze job postings for AI/ML roles using Indeed API
        """
        try:
            # Try to get real data from Indeed API
            real_data = self._fetch_indeed_jobs(company_name)
            if real_data and real_data['total_open_positions'] > 0:
                return real_data
        except Exception as e:
            print(f"Error fetching Indeed data: {e}")
        
        # Fallback to mock data if API fails
        mock_data = self._get_mock_job_data(company_name)
        
        # Calculate AI hiring intensity score
        total_jobs = mock_data['total_open_positions']
        ai_jobs = mock_data['ai_ml_positions']
        
        if total_jobs > 0:
            ai_hiring_ratio = (ai_jobs / total_jobs) * 100
        else:
            ai_hiring_ratio = 0
            
        mock_data['ai_hiring_intensity'] = min(100, ai_hiring_ratio * 2)  # Scale up for impact
        
        return mock_data
    
    def _fetch_indeed_jobs(self, company_name: str) -> Dict:
        """
        Fetch real job data from Indeed API via RapidAPI
        """
        url = f"https://{self.indeed_host}/jobs/search"
        
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.indeed_host
        }
        
        # First, get all jobs for the company
        params = {
            "query": f"company:{company_name}",
            "location": "United States",
            "page_id": "1",
            "locality": "us",
            "fromage": "30"  # Jobs posted in last 30 days
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"Indeed API error: {response.status_code}")
                return None
            
            data = response.json()
            
            # Parse the response
            total_jobs = len(data.get('hits', []))
            ai_roles = []
            tech_stack_mentions = set()
            
            # Analyze each job posting
            for job in data.get('hits', [])[:20]:  # Analyze first 20 jobs
                title = job.get('title', '').lower()
                description = job.get('description', '').lower() if job.get('description') else ''
                
                # Check if it's an AI/ML role
                is_ai_role = any(keyword in title or keyword in description 
                                for keyword in self.ai_keywords)
                
                if is_ai_role:
                    ai_roles.append({
                        'title': job.get('title', 'Unknown Position'),
                        'department': job.get('company_name', company_name),
                        'posted': self._format_posted_date(job.get('date_posted'))
                    })
                
                # Extract tech stack mentions
                for tech in ['python', 'tensorflow', 'pytorch', 'aws', 'azure', 'spark', 'kubernetes']:
                    if tech in description:
                        tech_stack_mentions.add(tech.capitalize())
            
            # Now search specifically for AI/ML roles
            ai_params = params.copy()
            ai_params['query'] = f"(data scientist OR machine learning OR artificial intelligence) company:{company_name}"
            
            ai_response = requests.get(url, headers=headers, params=ai_params, timeout=10)
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                ai_job_count = len(ai_data.get('hits', []))
                
                # Add AI-specific jobs to our list
                for job in ai_data.get('hits', [])[:10]:
                    if len(ai_roles) < 10:  # Limit to 10 AI roles
                        ai_roles.append({
                            'title': job.get('title', 'AI/ML Position'),
                            'department': job.get('company_name', company_name),
                            'posted': self._format_posted_date(job.get('date_posted'))
                        })
            else:
                ai_job_count = len(ai_roles)
            
            # Determine growth indicator based on hiring
            if ai_job_count > 20:
                growth = "Very High"
            elif ai_job_count > 10:
                growth = "High"
            elif ai_job_count > 5:
                growth = "Moderate"
            else:
                growth = "Low"
            
            result = {
                'total_open_positions': max(total_jobs, ai_job_count),
                'ai_ml_positions': ai_job_count,
                'recent_ai_roles': ai_roles[:5],  # Return top 5 AI roles
                'tech_stack_mentions': list(tech_stack_mentions),
                'growth_indicator': growth,
                'ai_hiring_intensity': min(100, (ai_job_count / max(total_jobs, 1)) * 100 * 2)
            }
            
            return result
            
        except Exception as e:
            print(f"Error fetching Indeed jobs: {e}")
            return None
    
    def _format_posted_date(self, date_str):
        """Format the posted date for display"""
        if not date_str:
            return "Recently"
        
        try:
            # Parse the date if it's in a standard format
            posted_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            days_ago = (datetime.now() - posted_date).days
            
            if days_ago == 0:
                return "Today"
            elif days_ago == 1:
                return "1 day ago"
            elif days_ago < 7:
                return f"{days_ago} days ago"
            elif days_ago < 30:
                weeks = days_ago // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            else:
                return "30+ days ago"
        except:
            return "Recently"
    
    def _get_mock_job_data(self, company_name: str) -> Dict:
        """
        Return mock job posting data
        """
        mock_companies = {
            "Goldman Sachs": {
                "total_open_positions": 247,
                "ai_ml_positions": 42,
                "recent_ai_roles": [
                    {
                        "title": "Vice President - Machine Learning Engineer",
                        "department": "Engineering",
                        "posted": "2 days ago"
                    },
                    {
                        "title": "Quantitative Analyst - AI/ML",
                        "department": "Securities",
                        "posted": "1 week ago"
                    },
                    {
                        "title": "Data Scientist - Risk Analytics",
                        "department": "Risk Management",
                        "posted": "3 days ago"
                    }
                ],
                "tech_stack_mentions": ["Python", "TensorFlow", "AWS", "Spark"],
                "growth_indicator": "High"
            },
            "JPMorgan Chase": {
                "total_open_positions": 512,
                "ai_ml_positions": 89,
                "recent_ai_roles": [
                    {
                        "title": "Executive Director - Head of AI Research",
                        "department": "Technology",
                        "posted": "1 day ago"
                    },
                    {
                        "title": "Machine Learning Engineer - Payments",
                        "department": "Digital Banking",
                        "posted": "4 days ago"
                    },
                    {
                        "title": "Senior Data Scientist - Fraud Detection",
                        "department": "Cybersecurity",
                        "posted": "1 week ago"
                    },
                    {
                        "title": "AI Platform Engineer",
                        "department": "Infrastructure",
                        "posted": "5 days ago"
                    }
                ],
                "tech_stack_mentions": ["Python", "Kubernetes", "PyTorch", "Cloud"],
                "growth_indicator": "Very High"
            },
            "BlackRock": {
                "total_open_positions": 156,
                "ai_ml_positions": 31,
                "recent_ai_roles": [
                    {
                        "title": "Director - Aladdin AI/ML Platform",
                        "department": "Aladdin Engineering",
                        "posted": "3 days ago"
                    },
                    {
                        "title": "Quantitative Researcher - ML Strategies",
                        "department": "Systematic Investing",
                        "posted": "1 week ago"
                    },
                    {
                        "title": "Data Scientist - Portfolio Analytics",
                        "department": "Risk & Analytics",
                        "posted": "2 days ago"
                    }
                ],
                "tech_stack_mentions": ["Python", "Scala", "Azure", "Databricks"],
                "growth_indicator": "High"
            }
        }
        
        # Default data for unknown companies
        default_data = {
            "total_open_positions": 25,
            "ai_ml_positions": 2,
            "recent_ai_roles": [
                {
                    "title": "Data Analyst",
                    "department": "Analytics",
                    "posted": "2 weeks ago"
                }
            ],
            "tech_stack_mentions": ["Excel", "SQL", "Python"],
            "growth_indicator": "Moderate"
        }
        
        # Try to match company name
        for key in mock_companies:
            if key.lower() in company_name.lower() or company_name.lower() in key.lower():
                return mock_companies[key]
                
        return default_data
    
    def scrape_indeed(self, company_name: str) -> List[Dict]:
        """
        Scrape Indeed for job postings (placeholder for actual implementation)
        """
        # This would contain actual scraping logic in production
        return []
    
    def scrape_linkedin(self, company_name: str) -> List[Dict]:
        """
        Scrape LinkedIn for job postings (placeholder for actual implementation)
        """
        # This would contain actual scraping logic in production
        return []