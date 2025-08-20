import requests
from typing import Dict, Optional
import json

class ClearbitService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://company.clearbit.com/v2/companies"
        
    def enrich_company(self, company_name: str) -> Optional[Dict]:
        """
        Fetch company data from Clearbit API
        """
        if not self.api_key:
            # Return mock data if no API key
            return self._get_mock_data(company_name)
            
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        params = {
            'name': company_name
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/find",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_mock_data(company_name)
                
        except Exception as e:
            print(f"Clearbit API error: {e}")
            return self._get_mock_data(company_name)
    
    def _get_mock_data(self, company_name: str) -> Dict:
        """
        Return mock data for demo purposes
        """
        mock_companies = {
            "Goldman Sachs": {
                "name": "Goldman Sachs",
                "domain": "goldmansachs.com",
                "industry": "Financial Services",
                "employeeCount": 45000,
                "marketCap": 120000000000,
                "description": "Leading global investment banking and financial services firm",
                "tags": ["Investment Banking", "Asset Management", "Trading"],
                "techStack": ["Python", "Java", "React", "AWS"],
                "fundingTotal": None,
                "location": {
                    "city": "New York",
                    "state": "NY",
                    "country": "US"
                }
            },
            "JPMorgan Chase": {
                "name": "JPMorgan Chase & Co.",
                "domain": "jpmorganchase.com",
                "industry": "Financial Services",
                "employeeCount": 290000,
                "marketCap": 500000000000,
                "description": "Largest bank in the United States and leader in investment banking",
                "tags": ["Banking", "Investment Management", "Fintech"],
                "techStack": ["Python", "Java", "Kubernetes", "Cloud"],
                "fundingTotal": None,
                "location": {
                    "city": "New York",
                    "state": "NY",
                    "country": "US"
                }
            },
            "BlackRock": {
                "name": "BlackRock",
                "domain": "blackrock.com",
                "industry": "Asset Management",
                "employeeCount": 18000,
                "marketCap": 110000000000,
                "description": "World's largest asset manager with focus on technology-driven investing",
                "tags": ["Asset Management", "ETFs", "Risk Management"],
                "techStack": ["Python", "Aladdin", "Cloud", "Machine Learning"],
                "fundingTotal": None,
                "location": {
                    "city": "New York",
                    "state": "NY",
                    "country": "US"
                }
            }
        }
        
        # Default data for unknown companies
        default_data = {
            "name": company_name,
            "domain": f"{company_name.lower().replace(' ', '')}.com",
            "industry": "Technology",
            "employeeCount": 500,
            "marketCap": 1000000000,
            "description": f"Information about {company_name}",
            "tags": ["Technology", "Software"],
            "techStack": ["Python", "JavaScript", "Cloud"],
            "fundingTotal": 50000000,
            "location": {
                "city": "San Francisco",
                "state": "CA",
                "country": "US"
            }
        }
        
        # Try to match company name
        for key in mock_companies:
            if key.lower() in company_name.lower() or company_name.lower() in key.lower():
                return mock_companies[key]
                
        return default_data