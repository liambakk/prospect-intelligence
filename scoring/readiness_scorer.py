from typing import Dict
from config import Config

class ReadinessScorer:
    def __init__(self):
        self.weights = Config.SCORING_WEIGHTS
        self.industry_benchmarks = Config.INDUSTRY_BENCHMARKS
        
    def calculate_ai_readiness_score(self, company_data: Dict) -> Dict:
        """
        Calculate comprehensive AI readiness score
        """
        scores = {}
        
        # 1. Tech Hiring Score (25%)
        job_data = company_data.get('job_analysis', {})
        scores['tech_hiring'] = self._calculate_hiring_score(job_data)
        
        # 2. AI Mentions Score (25%)
        website_data = company_data.get('website_analysis', {})
        news_data = company_data.get('news_analysis', {})
        scores['ai_mentions'] = self._calculate_mentions_score(website_data, news_data)
        
        # 3. Company Growth Score (20%)
        company_info = company_data.get('company_info', {})
        scores['company_growth'] = self._calculate_growth_score(company_info)
        
        # 4. Industry Adoption Score (15%)
        industry = company_info.get('industry', 'default')
        scores['industry_adoption'] = self._get_industry_benchmark(industry)
        
        # 5. Tech Modernization Score (15%)
        scores['tech_modernization'] = self._calculate_modernization_score(
            website_data, job_data
        )
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * self.weights[key] 
            for key in scores if key in self.weights
        )
        
        # Determine readiness level
        readiness_level = self._determine_readiness_level(total_score)
        
        return {
            'total_score': round(total_score, 1),
            'component_scores': scores,
            'readiness_level': readiness_level,
            'confidence': self._calculate_confidence(company_data)
        }
    
    def _calculate_hiring_score(self, job_data: Dict) -> float:
        """Calculate score based on AI/ML hiring activity"""
        if not job_data:
            return 30  # Default low score
            
        ai_intensity = job_data.get('ai_hiring_intensity', 0)
        ai_positions = job_data.get('ai_ml_positions', 0)
        
        # Normalize to 0-100
        if ai_positions == 0:
            return 20
        elif ai_positions < 5:
            return 40
        elif ai_positions < 20:
            return 60
        elif ai_positions < 50:
            return 80
        else:
            return min(100, 80 + (ai_positions - 50) * 0.4)
    
    def _calculate_mentions_score(self, website_data: Dict, news_data: Dict) -> float:
        """Calculate score based on AI mentions in website and news"""
        website_mentions = website_data.get('ai_mentions_count', 0)
        news_ai_articles = news_data.get('ai_related_articles', 0)
        
        # Website component (60% of mentions score)
        if website_mentions == 0:
            website_score = 10
        elif website_mentions < 10:
            website_score = 30
        elif website_mentions < 30:
            website_score = 50
        elif website_mentions < 50:
            website_score = 70
        else:
            website_score = min(100, 70 + website_mentions * 0.6)
            
        # News component (40% of mentions score)
        if news_ai_articles == 0:
            news_score = 10
        elif news_ai_articles < 3:
            news_score = 30
        elif news_ai_articles < 7:
            news_score = 60
        elif news_ai_articles < 12:
            news_score = 80
        else:
            news_score = min(100, 80 + news_ai_articles * 1.5)
            
        return website_score * 0.6 + news_score * 0.4
    
    def _calculate_growth_score(self, company_info: Dict) -> float:
        """Calculate score based on company size and growth indicators"""
        employee_count = company_info.get('employeeCount', 100)
        market_cap = company_info.get('marketCap', 0)
        
        # Size component
        if employee_count < 100:
            size_score = 30
        elif employee_count < 1000:
            size_score = 50
        elif employee_count < 10000:
            size_score = 70
        else:
            size_score = 85
            
        # Market cap component (if available)
        if market_cap > 100000000000:  # >$100B
            cap_score = 90
        elif market_cap > 10000000000:  # >$10B
            cap_score = 70
        elif market_cap > 1000000000:  # >$1B
            cap_score = 50
        else:
            cap_score = 30
            
        # Average the scores
        return (size_score + cap_score) / 2
    
    def _get_industry_benchmark(self, industry: str) -> float:
        """Get industry-specific AI adoption benchmark"""
        # Normalize industry string
        industry_lower = industry.lower()
        
        for key in self.industry_benchmarks:
            if key in industry_lower or industry_lower in key:
                return self.industry_benchmarks[key]
                
        return self.industry_benchmarks['default']
    
    def _calculate_modernization_score(self, website_data: Dict, job_data: Dict) -> float:
        """Calculate tech modernization score"""
        tech_stack = website_data.get('tech_stack_visible', [])
        innovation_score = website_data.get('innovation_score', 30)
        tech_roles = job_data.get('tech_stack_mentions', [])
        
        # Modern tech stack indicators
        modern_tech = ['cloud', 'kubernetes', 'docker', 'react', 'python', 
                      'tensorflow', 'pytorch', 'aws', 'azure', 'gcp']
        
        # Count modern technologies
        tech_count = sum(1 for tech in tech_stack + tech_roles 
                        if any(modern in tech.lower() for modern in modern_tech))
        
        # Calculate score
        if tech_count == 0:
            tech_score = 20
        elif tech_count < 3:
            tech_score = 40
        elif tech_count < 5:
            tech_score = 60
        elif tech_count < 8:
            tech_score = 80
        else:
            tech_score = 95
            
        # Combine with innovation score
        return (tech_score * 0.6 + innovation_score * 0.4)
    
    def _determine_readiness_level(self, score: float) -> str:
        """Determine readiness level based on score"""
        if score >= 80:
            return "Very High - Prime candidate for ModelML"
        elif score >= 65:
            return "High - Strong potential for AI adoption"
        elif score >= 50:
            return "Moderate - Building AI capabilities"
        elif score >= 35:
            return "Low - Early stage of AI journey"
        else:
            return "Very Low - Not yet ready for advanced AI"
    
    def _calculate_confidence(self, company_data: Dict) -> str:
        """Calculate confidence level based on data completeness"""
        data_points = [
            company_data.get('company_info'),
            company_data.get('job_analysis'),
            company_data.get('news_analysis'),
            company_data.get('website_analysis')
        ]
        
        available = sum(1 for dp in data_points if dp and len(dp) > 2)
        
        if available == 4:
            return "High"
        elif available >= 3:
            return "Medium"
        else:
            return "Low"