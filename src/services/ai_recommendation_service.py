"""
AI-Powered Recommendation Service using OpenAI
Generates personalized sales recommendations based on company analysis
"""

import os
import logging
from typing import Dict, Any, List, Optional
import httpx
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class AIRecommendationService:
    """
    Service for generating AI-powered sales recommendations using OpenAI
    """
    
    def __init__(self):
        """Initialize OpenAI service"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4-turbo-preview"  # Or gpt-3.5-turbo for faster/cheaper
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Will use template-based recommendations.")
    
    async def generate_sales_recommendations(
        self,
        company_name: str,
        ai_readiness_score: int,
        component_scores: Dict[str, int],
        company_data: Dict[str, Any],
        decision_makers: List[Dict[str, Any]],
        is_financial: bool = False
    ) -> Dict[str, Any]:
        """
        Generate AI-powered sales recommendations based on analysis
        
        Args:
            company_name: Name of the company
            ai_readiness_score: Overall AI readiness score (0-100)
            component_scores: Individual component scores
            company_data: All collected company data
            decision_makers: List of identified decision makers
            is_financial: Whether it's a financial services company
            
        Returns:
            Dictionary with AI-generated recommendations
        """
        
        if not self.api_key:
            logger.info("Using template-based recommendations (no OpenAI key)")
            return self._get_template_recommendations(
                company_name, ai_readiness_score, component_scores, is_financial
            )
        
        try:
            # Prepare context for AI
            context = self._prepare_context(
                company_name, ai_readiness_score, component_scores, 
                company_data, decision_makers, is_financial
            )
            
            # Generate recommendations using OpenAI
            recommendations = await self._call_openai(context)
            
            if recommendations:
                logger.info(f"Generated AI-powered recommendations for {company_name}")
                return recommendations
            else:
                logger.warning("OpenAI call failed, using template recommendations")
                return self._get_template_recommendations(
                    company_name, ai_readiness_score, component_scores, is_financial
                )
                
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return self._get_template_recommendations(
                company_name, ai_readiness_score, component_scores, is_financial
            )
    
    def _prepare_context(
        self,
        company_name: str,
        ai_readiness_score: int,
        component_scores: Dict[str, int],
        company_data: Dict[str, Any],
        decision_makers: List[Dict[str, Any]],
        is_financial: bool
    ) -> str:
        """Prepare context for OpenAI prompt"""
        
        # Extract key information
        job_data = company_data.get("job_postings", {})
        news_data = company_data.get("news_insights", {})
        tech_signals = company_data.get("tech_signals", {})
        
        context = f"""
Company Analysis for {company_name}:

AI Readiness Score: {ai_readiness_score}/100
Industry: {'Financial Services' if is_financial else 'General'}

Component Scores:
"""
        
        # Add component scores
        for component, score in component_scores.items():
            context += f"- {component.replace('_', ' ').title()}: {score}/100\n"
        
        # Add job posting insights
        if job_data:
            context += f"""
            
Hiring Signals:
- Total tech jobs: {job_data.get('total_jobs', 0)}
- AI/ML roles: {job_data.get('ai_ml_jobs', 0)}
- AI hiring intensity: {job_data.get('ai_hiring_intensity', 'low')}
"""
        
        # Add tech signals
        if tech_signals:
            context += f"""
            
Technology Indicators:
- AI mentions on website: {tech_signals.get('ai_mentions', 0)}
- Tech stack detected: {', '.join(tech_signals.get('tech_stack', [])[:5])}
"""
        
        # Add news insights
        if news_data:
            context += f"""
            
Recent News & Trends:
- Articles analyzed: {news_data.get('articles_analyzed', 0)}
- Tech focus score: {news_data.get('tech_focus_score', 0)}/100
- Recent trends: {', '.join(news_data.get('recent_trends', [])[:3])}
"""
        
        # Add decision makers
        if decision_makers:
            context += f"""
            
Key Decision Makers Identified: {len(decision_makers)}
Top roles: {', '.join([dm.get('title', '') for dm in decision_makers[:3]])}
"""
        
        return context
    
    async def _call_openai(self, context: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI API to generate recommendations"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
You are a sales strategist for ModelML, an AI infrastructure platform that helps enterprises deploy and scale AI models.

Based on the following company analysis, generate specific, actionable sales recommendations.

{context}

Generate a JSON response with the following structure:
{{
    "sales_strategy": "High-level approach (2-3 sentences)",
    "priority_level": "high/medium/low",
    "estimated_deal_size": "Range like $500K-$1M",
    "timeline": "Immediate/3-6 months/6-12 months",
    "key_talking_points": [
        "Specific value prop 1",
        "Specific value prop 2",
        "Specific value prop 3"
    ],
    "recommended_use_cases": [
        "Use case 1 based on their industry/needs",
        "Use case 2",
        "Use case 3"
    ],
    "objection_handling": [
        {{"objection": "Likely concern 1", "response": "How to address it"}},
        {{"objection": "Likely concern 2", "response": "How to address it"}}
    ],
    "next_steps": [
        "Immediate action 1",
        "Follow-up action 2",
        "Long-term action 3"
    ],
    "competitive_positioning": "How ModelML compares to alternatives they might consider",
    "success_metrics": [
        "KPI they care about 1",
        "KPI they care about 2"
    ]
}}

IMPORTANT RULES for key_talking_points:
- Do NOT start with "You're", "Your", "You have", "You are", etc.
- Start with factual statements or direct benefits
- Example: Instead of "You're hiring aggressively", write "Aggressive AI talent hiring (42 open positions)"
- Example: Instead of "Your recent initiative", write "Recent Goldman Sachs AI-Powered Trading Platform aligns with ModelML"
- Make them crisp, factual, and professional

Make the recommendations specific to their AI readiness level and industry. Be concrete and actionable.
"""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a B2B sales strategist specializing in AI/ML infrastructure sales."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    try:
                        recommendations = json.loads(content)
                        return recommendations
                    except json.JSONDecodeError:
                        logger.error("Failed to parse OpenAI JSON response")
                        return None
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None
    
    async def generate_personalized_outreach(
        self,
        decision_maker: Dict[str, Any],
        company_name: str,
        ai_readiness_score: int,
        key_insights: List[str]
    ) -> Dict[str, Any]:
        """
        Generate personalized outreach messaging for a specific decision maker
        
        Args:
            decision_maker: Decision maker information
            company_name: Company name
            ai_readiness_score: AI readiness score
            key_insights: Key insights about the company
            
        Returns:
            Personalized outreach strategy
        """
        
        if not self.api_key:
            return self._get_template_outreach(decision_maker, company_name)
        
        try:
            prompt = f"""
Generate a personalized outreach strategy for:

Decision Maker: {decision_maker.get('name', 'Executive')}
Title: {decision_maker.get('title', 'Unknown')}
Company: {company_name}
AI Readiness: {ai_readiness_score}/100

Key Insights:
{chr(10).join(['- ' + insight for insight in key_insights[:5]])}

Create a JSON response with:
{{
    "email_subject_lines": [3 compelling subject lines],
    "opening_line": "Personalized opening that references their role/company",
    "value_proposition": "2-3 sentences on ModelML's specific value for them",
    "social_proof": "Relevant customer success story or metric",
    "call_to_action": "Specific next step",
    "linkedin_message": "Short LinkedIn outreach message (under 300 chars)",
    "talking_points": [3 specific points for a call]
}}

IMPORTANT: For talking_points, do NOT start with "You", "Your", etc. Use factual, professional language.
"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",  # Faster for simple outreach
                "messages": [
                    {"role": "system", "content": "You are a B2B sales expert crafting personalized outreach."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 800,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return json.loads(content)
                    
        except Exception as e:
            logger.error(f"Error generating personalized outreach: {e}")
        
        return self._get_template_outreach(decision_maker, company_name)
    
    def _get_template_recommendations(
        self,
        company_name: str,
        ai_readiness_score: int,
        component_scores: Dict[str, int],
        is_financial: bool
    ) -> Dict[str, Any]:
        """Fallback template-based recommendations"""
        
        # Determine priority based on score
        if ai_readiness_score >= 70:
            priority = "high"
            timeline = "Immediate"
            deal_size = "$1M-$3M"
            strategy = f"{company_name} shows strong AI readiness. Position ModelML as the platform to scale their existing AI initiatives enterprise-wide."
        elif ai_readiness_score >= 40:
            priority = "medium"
            timeline = "3-6 months"
            deal_size = "$500K-$1M"
            strategy = f"{company_name} is building AI capabilities. ModelML can accelerate their journey with pre-built models and infrastructure."
        else:
            priority = "low"
            timeline = "6-12 months"
            deal_size = "$250K-$500K"
            strategy = f"{company_name} is early in AI adoption. Focus on education and quick wins with ModelML's turnkey solutions."
        
        # Industry-specific talking points
        if is_financial:
            talking_points = [
                "Regulatory-compliant AI models designed for financial services",
                "Pre-built fraud detection and risk assessment models available",
                "SOC 2 Type II certification with bank-grade security standards"
            ]
            use_cases = [
                "Real-time fraud detection and prevention",
                "Credit risk assessment and underwriting",
                "Regulatory compliance automation"
            ]
        else:
            talking_points = [
                "AI deployment timeline reduced from months to weeks",
                "Seamless scaling from prototype to production environment",
                "Enterprise-grade security and governance built-in"
            ]
            use_cases = [
                "Customer service automation",
                "Predictive analytics for operations",
                "Document processing and extraction"
            ]
        
        return {
            "sales_strategy": strategy,
            "priority_level": priority,
            "estimated_deal_size": deal_size,
            "timeline": timeline,
            "key_talking_points": talking_points,
            "recommended_use_cases": use_cases,
            "objection_handling": [
                {
                    "objection": "We don't have AI expertise",
                    "response": "ModelML provides pre-built models and full support, no ML expertise required"
                },
                {
                    "objection": "Concerned about cost",
                    "response": "ModelML typically delivers ROI within 6 months through efficiency gains"
                }
            ],
            "next_steps": [
                f"Schedule discovery call with {company_name}'s CTO/CDO",
                "Prepare customized demo focusing on their use cases",
                "Share relevant case studies from their industry"
            ],
            "competitive_positioning": "Unlike generic platforms, ModelML provides industry-specific models and compliance features",
            "success_metrics": [
                "Time to deploy first AI model",
                "Cost savings from automation",
                "Improvement in decision accuracy"
            ]
        }
    
    def _get_template_outreach(
        self,
        decision_maker: Dict[str, Any],
        company_name: str
    ) -> Dict[str, Any]:
        """Fallback template-based outreach"""
        
        title = decision_maker.get('title', 'Executive')
        name = decision_maker.get('name', 'there')
        
        return {
            "email_subject_lines": [
                f"Quick question about {company_name}'s AI initiatives",
                f"{name.split()[0] if name != 'there' else 'Hi'} - 15 min to discuss AI scaling?",
                f"How {company_name} can deploy AI 10x faster"
            ],
            "opening_line": f"Hi {name}, I noticed {company_name} is expanding its tech capabilities and thought you might be interested in how we're helping similar companies scale their AI initiatives.",
            "value_proposition": f"ModelML helps companies like {company_name} deploy production-ready AI models in weeks instead of months. Our platform handles the infrastructure complexity so your team can focus on business value.",
            "social_proof": "We recently helped a similar company reduce their AI deployment time by 75% while improving model accuracy by 30%.",
            "call_to_action": "Would you be open to a brief 15-minute call next week to explore if ModelML could accelerate your AI roadmap?",
            "linkedin_message": f"Hi {name.split()[0] if name != 'there' else ''}, I help companies like {company_name} scale AI faster. Worth a quick chat?",
            "talking_points": [
                f"How ModelML aligns with {company_name}'s digital transformation goals",
                "Quick wins we can deliver in the first 30 days",
                "ROI and success metrics from similar implementations"
            ]
        }