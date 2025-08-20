import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLEARBIT_API_KEY = os.getenv('CLEARBIT_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///prospect_intelligence.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Scoring weights
    SCORING_WEIGHTS = {
        'tech_hiring': 0.25,
        'ai_mentions': 0.25,
        'company_growth': 0.20,
        'industry_adoption': 0.15,
        'tech_modernization': 0.15
    }
    
    # Industry AI adoption benchmarks (0-100)
    INDUSTRY_BENCHMARKS = {
        'financial_services': 75,
        'technology': 90,
        'healthcare': 65,
        'retail': 60,
        'manufacturing': 55,
        'energy': 50,
        'default': 60
    }