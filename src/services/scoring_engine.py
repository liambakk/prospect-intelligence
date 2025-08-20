"""
AI Readiness Scoring Engine
Combines signals from multiple sources to calculate comprehensive score
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScoringWeights:
    """Configurable weights for scoring components"""
    tech_hiring: float = 0.25      # Job postings with AI/ML roles
    ai_mentions: float = 0.25      # AI/ML keyword frequency
    company_size: float = 0.20     # Company size and growth
    industry_adoption: float = 0.15 # Industry AI maturity
    tech_modernization: float = 0.15 # Modern tech stack


class AIReadinessScoringEngine:
    """
    Calculates AI readiness scores based on multiple data signals
    """
    
    # Industry AI adoption benchmarks (0-100)
    INDUSTRY_SCORES = {
        "technology": 85,
        "artificial intelligence": 95,
        "software": 75,
        "financial services": 70,
        "banking": 65,
        "investment banking": 70,
        "internet": 80,
        "e-commerce": 75,
        "healthcare": 60,
        "retail": 55,
        "manufacturing": 50,
        "insurance": 60,
        "consulting": 70,
        "education": 45,
        "government": 40,
        "non-profit": 35,
        "default": 50
    }
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
    
    def calculate_ai_readiness_score(
        self,
        hunter_data: Optional[Dict[str, Any]] = None,
        web_scraping_data: Optional[Dict[str, Any]] = None,
        clearbit_data: Optional[Dict[str, Any]] = None,
        job_posting_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive AI readiness score
        
        Returns:
            Dictionary with overall_score, component_scores, confidence, and recommendations
        """
        
        component_scores = {}
        confidence_factors = []
        
        # 1. Tech Hiring Score (25%)
        tech_hiring_score = self._calculate_tech_hiring_score(
            hunter_data, web_scraping_data, job_posting_data
        )
        component_scores["tech_hiring"] = tech_hiring_score
        # Only add confidence if we have actual data (not default score of 30)
        if (hunter_data and hunter_data.get("key_contacts")) or \
           (web_scraping_data and web_scraping_data.get("careers_signals")) or \
           (job_posting_data and job_posting_data.get("total_jobs_found", 0) > 0):
            confidence_factors.append(0.9)
        
        # 2. AI Mentions Score (25%)
        ai_mentions_score = self._calculate_ai_mentions_score(
            web_scraping_data, news_data
        )
        component_scores["ai_mentions"] = ai_mentions_score
        # Only add confidence if we have actual web/news data
        if web_scraping_data or news_data:
            confidence_factors.append(0.8)
        
        # 3. Company Size Score (20%)
        company_size_score = self._calculate_company_size_score(
            hunter_data, clearbit_data
        )
        component_scores["company_size"] = company_size_score
        # Only add confidence if we have size data
        if (hunter_data and hunter_data.get("size")) or \
           (clearbit_data and clearbit_data.get("employees")):
            confidence_factors.append(0.7)
        
        # 4. Industry Adoption Score (15%)
        industry_score = self._calculate_industry_score(
            hunter_data, clearbit_data
        )
        component_scores["industry_adoption"] = industry_score
        # Only add confidence if we have industry data
        if (hunter_data and hunter_data.get("industry")) or \
           (clearbit_data and clearbit_data.get("industry")):
            confidence_factors.append(0.85)
        
        # 5. Tech Modernization Score (15%)
        tech_modern_score = self._calculate_tech_modernization_score(
            web_scraping_data, clearbit_data
        )
        component_scores["tech_modernization"] = tech_modern_score
        # Only add confidence if we have tech stack data
        if (web_scraping_data and web_scraping_data.get("tech_stack_detected")) or \
           (clearbit_data and clearbit_data.get("tech_stack")):
            confidence_factors.append(0.75)
        
        # Calculate weighted overall score
        overall_score = (
            self.weights.tech_hiring * component_scores["tech_hiring"] +
            self.weights.ai_mentions * component_scores["ai_mentions"] +
            self.weights.company_size * component_scores["company_size"] +
            self.weights.industry_adoption * component_scores["industry_adoption"] +
            self.weights.tech_modernization * component_scores["tech_modernization"]
        )
        
        # Calculate confidence based on data availability
        confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.3
        
        # Generate recommendations
        recommendations = self._generate_recommendations(component_scores, overall_score)
        
        # Determine readiness category
        readiness_category = self._get_readiness_category(overall_score)
        
        return {
            "overall_score": round(overall_score),
            "component_scores": component_scores,
            "confidence": round(confidence, 2),
            "readiness_category": readiness_category,
            "recommendations": recommendations,
            "key_strengths": self._identify_strengths(component_scores),
            "improvement_areas": self._identify_weaknesses(component_scores)
        }
    
    def _calculate_tech_hiring_score(
        self, 
        hunter_data: Optional[Dict], 
        web_data: Optional[Dict],
        job_data: Optional[Dict]
    ) -> int:
        """Calculate score based on technical hiring signals"""
        score = 0
        signals = 0
        
        # Job posting data (highest weight - most direct signal)
        if job_data:
            ai_ml_jobs = job_data.get("ai_ml_jobs_count", 0)
            tech_jobs = job_data.get("tech_jobs_count", 0)
            hiring_intensity = job_data.get("ai_hiring_intensity", "none")
            
            # Score based on AI/ML job count
            if ai_ml_jobs >= 10:
                score += 40
            elif ai_ml_jobs >= 5:
                score += 30
            elif ai_ml_jobs >= 2:
                score += 20
            elif ai_ml_jobs >= 1:
                score += 10
            
            # Additional score for general tech hiring
            if tech_jobs >= 20:
                score += 20
            elif tech_jobs >= 10:
                score += 15
            elif tech_jobs >= 5:
                score += 10
            elif tech_jobs >= 1:
                score += 5
            
            # Bonus for high AI hiring intensity
            if hiring_intensity == "very_high":
                score += 15
            elif hiring_intensity == "high":
                score += 10
            elif hiring_intensity == "moderate":
                score += 5
            
            signals += 1
        
        # Hunter.io executive contacts
        if hunter_data and hunter_data.get("key_contacts"):
            tech_executives = [
                c for c in hunter_data["key_contacts"] 
                if any(role in c.get("title", "").lower() 
                      for role in ["cto", "engineer", "data", "ai", "ml", "tech"])
            ]
            if tech_executives:
                score += min(len(tech_executives) * 10, 30)  # Reduced weight
                signals += 1
        
        # Web scraping careers signals
        if web_data and web_data.get("careers_signals"):
            careers = web_data["careers_signals"]
            if careers.get("ai_roles"):
                score += min(len(careers["ai_roles"]) * 8, 25)  # Reduced weight
                signals += 1
            if careers.get("tech_roles_count", 0) > 5:
                score += 10  # Reduced weight
                signals += 1
        
        # Normalize if we have signals
        if signals > 0:
            return min(score, 100)
        
        return 30  # Default if no data
    
    def _calculate_ai_mentions_score(
        self,
        web_data: Optional[Dict],
        news_data: Optional[Dict]
    ) -> int:
        """Calculate score based on AI/ML mentions in web content and news"""
        score = 0
        data_sources = 0
        
        # Score from web scraping
        if web_data:
            ai_mentions = web_data.get("ai_mentions_count", 0)
            if ai_mentions > 30:
                web_score = 90
            elif ai_mentions > 20:
                web_score = 75
            elif ai_mentions > 10:
                web_score = 60
            elif ai_mentions > 5:
                web_score = 45
            elif ai_mentions > 0:
                web_score = 30
            else:
                web_score = 15
            score += web_score
            data_sources += 1
        
        # Score from news articles
        if news_data:
            tech_focus = news_data.get("tech_focus_score", 0)
            articles_count = news_data.get("articles_processed", 0)
            
            if tech_focus > 0 and articles_count > 0:
                # Use tech focus score directly (already 0-100)
                news_score = tech_focus
                score += news_score
                data_sources += 1
            
            # Bonus for recent AI trends in news
            trends = news_data.get("recent_trends", [])
            if any("artificial intelligence" in t.lower() or "machine learning" in t.lower() for t in trends):
                score += 10
        
        # Average the scores if we have multiple sources
        if data_sources > 0:
            score = score / data_sources
        
        return min(int(score), 100)
    
    def _calculate_company_size_score(
        self,
        hunter_data: Optional[Dict],
        clearbit_data: Optional[Dict]
    ) -> int:
        """Calculate score based on company size"""
        
        # Try to get size from either source
        size = None
        if hunter_data and hunter_data.get("size"):
            size = hunter_data["size"]
        elif clearbit_data and clearbit_data.get("employees"):
            employees = clearbit_data["employees"]
            if employees > 10000:
                size = "10000+"
            elif employees > 1000:
                size = "1000-5000"
            elif employees > 100:
                size = "100-1000"
            else:
                size = "11-50"
        
        # Score based on size
        if size:
            size_str = str(size)
            if "10000+" in size_str:
                return 85
            elif "5000" in size_str or "1000-5000" in size_str:
                return 70
            elif "500" in size_str or "100-1000" in size_str or "100-500" in size_str:
                return 60
            elif "50" in size_str or "11-50" in size_str:
                return 50
            elif "1-10" in size_str:
                return 40
            else:
                return 50  # Default for unrecognized formats
        
        return 50  # Default medium score
    
    def _calculate_industry_score(
        self,
        hunter_data: Optional[Dict],
        clearbit_data: Optional[Dict]
    ) -> int:
        """Calculate score based on industry AI adoption"""
        
        industry = None
        if hunter_data and hunter_data.get("industry"):
            industry = hunter_data["industry"]
        elif clearbit_data and clearbit_data.get("industry"):
            industry = clearbit_data["industry"]
        
        if industry:
            industry_lower = industry.lower()
            
            # Check for exact matches first
            for key, score in self.INDUSTRY_SCORES.items():
                if key in industry_lower:
                    return score
        
        return self.INDUSTRY_SCORES["default"]
    
    def _calculate_tech_modernization_score(
        self,
        web_data: Optional[Dict],
        clearbit_data: Optional[Dict]
    ) -> int:
        """Calculate score based on technology stack modernization"""
        
        tech_stack = []
        
        # Get tech stack from web scraping
        if web_data and web_data.get("tech_stack_detected"):
            tech_stack.extend(web_data["tech_stack_detected"])
        
        # Get tech stack from Clearbit
        if clearbit_data and clearbit_data.get("tech_stack"):
            tech_stack.extend(clearbit_data["tech_stack"])
        
        # Remove duplicates
        tech_stack = list(set([t.lower() for t in tech_stack]))
        
        # Score based on modern tech adoption
        score = 0
        
        # Cloud platforms
        cloud_techs = ["aws", "azure", "gcp", "google cloud", "kubernetes", "docker"]
        cloud_count = sum(1 for tech in tech_stack if any(c in tech for c in cloud_techs))
        score += min(cloud_count * 15, 30)
        
        # Modern languages/frameworks
        modern_techs = ["react", "vue", "angular", "node", "python", "go", "rust", "typescript"]
        modern_count = sum(1 for tech in tech_stack if any(m in tech for m in modern_techs))
        score += min(modern_count * 10, 30)
        
        # AI/ML tools
        ai_techs = ["tensorflow", "pytorch", "scikit", "jupyter", "spark", "databricks"]
        ai_count = sum(1 for tech in tech_stack if any(a in tech for a in ai_techs))
        score += min(ai_count * 20, 40)
        
        return min(score, 100) if tech_stack else 40
    
    def _get_readiness_category(self, score: float) -> str:
        """Categorize readiness level"""
        if score >= 80:
            return "AI-Ready Leader"
        elif score >= 65:
            return "Strong Potential"
        elif score >= 50:
            return "Emerging Interest"
        elif score >= 35:
            return "Early Stage"
        else:
            return "Not Yet Ready"
    
    def _generate_recommendations(self, component_scores: Dict[str, int], overall_score: float) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if component_scores["tech_hiring"] < 50:
            recommendations.append("Consider hiring AI/ML talent to build internal capabilities")
        
        if component_scores["ai_mentions"] < 40:
            recommendations.append("Develop clear AI strategy and communicate it publicly")
        
        if component_scores["tech_modernization"] < 50:
            recommendations.append("Modernize technology stack with cloud and AI-ready infrastructure")
        
        if overall_score >= 70:
            recommendations.append("Ready for advanced AI implementation - consider ModelML's platform")
        elif overall_score >= 50:
            recommendations.append("Good foundation - start with pilot AI projects")
        else:
            recommendations.append("Focus on digital transformation before AI adoption")
        
        return recommendations
    
    def _identify_strengths(self, component_scores: Dict[str, int]) -> List[str]:
        """Identify key strengths"""
        strengths = []
        
        for component, score in component_scores.items():
            if score >= 70:
                if component == "tech_hiring":
                    strengths.append("Strong technical team")
                elif component == "ai_mentions":
                    strengths.append("Clear AI focus")
                elif component == "company_size":
                    strengths.append("Sufficient scale for AI")
                elif component == "industry_adoption":
                    strengths.append("AI-forward industry")
                elif component == "tech_modernization":
                    strengths.append("Modern tech stack")
        
        return strengths if strengths else ["Building AI foundation"]
    
    def _identify_weaknesses(self, component_scores: Dict[str, int]) -> List[str]:
        """Identify improvement areas"""
        weaknesses = []
        
        for component, score in component_scores.items():
            if score < 40:
                if component == "tech_hiring":
                    weaknesses.append("Limited AI talent")
                elif component == "ai_mentions":
                    weaknesses.append("Low AI visibility")
                elif component == "company_size":
                    weaknesses.append("Scale considerations")
                elif component == "industry_adoption":
                    weaknesses.append("Industry AI maturity")
                elif component == "tech_modernization":
                    weaknesses.append("Legacy technology")
        
        return weaknesses if weaknesses else ["Continue AI journey"]