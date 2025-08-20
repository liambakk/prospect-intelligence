"""
Financial Services AI Readiness Scoring Engine
Specialized scoring for banks, asset managers, and financial institutions
Tailored for ModelML's financial services focus
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from .scoring_engine import AIReadinessScoringEngine, ScoringWeights

logger = logging.getLogger(__name__)


@dataclass
class FinancialScoringWeights:
    """Weights optimized for financial services AI readiness"""
    regulatory_compliance: float = 0.20    # Regulatory readiness & compliance
    data_governance: float = 0.20          # Data infrastructure & governance
    quant_risk_capabilities: float = 0.15  # Quantitative & risk modeling
    aml_kyc_capabilities: float = 0.15    # AML/KYC & financial crime
    tech_modernization: float = 0.15      # Core systems & infrastructure
    ai_ml_maturity: float = 0.15          # AI/ML teams & initiatives


class FinancialAIReadinessScoringEngine(AIReadinessScoringEngine):
    """
    Specialized AI readiness scoring for financial services companies
    Extends base scoring with financial-specific criteria
    """
    
    # Financial sub-sector AI adoption benchmarks (0-100)
    FINANCIAL_SECTOR_SCORES = {
        # High AI adoption
        "fintech": 90,
        "hedge fund": 85,
        "payment processor": 80,
        "investment banking": 75,
        "trading firm": 75,
        
        # Medium AI adoption
        "asset management": 70,
        "wealth management": 70,
        "private equity": 68,
        "retail banking": 65,
        "commercial banking": 65,
        "investment bank": 70,
        
        # Lower AI adoption
        "insurance": 60,
        "reinsurance": 58,
        "regional bank": 55,
        "community bank": 50,
        "credit union": 45,
        
        # Generic categories
        "financial services": 65,
        "banking": 65,
        "finance": 60,
        "default": 55
    }
    
    # Regulatory compliance keywords
    REGULATORY_KEYWORDS = [
        # Major regulations
        "basel iii", "basel iv", "mifid ii", "gdpr", "dodd-frank",
        "eu ai act", "psd2", "solvency ii", "ifrs 9", "cecl",
        
        # Compliance concepts
        "regulatory reporting", "compliance automation", "regtech",
        "supervisory technology", "suptech", "model risk management",
        "sr 11-7", "model validation", "model governance",
        "explainable ai", "fair lending", "disparate impact"
    ]
    
    # Data governance keywords
    DATA_GOVERNANCE_KEYWORDS = [
        "data governance", "data quality", "data lineage", "data catalog",
        "master data management", "mdm", "single source of truth",
        "data lake", "data warehouse", "data mesh", "data fabric",
        "metadata management", "data stewardship", "data privacy",
        "data classification", "data retention", "data archival"
    ]
    
    # Quantitative & risk keywords
    QUANT_RISK_KEYWORDS = [
        # Risk types
        "credit risk", "market risk", "operational risk", "liquidity risk",
        "counterparty risk", "concentration risk", "model risk",
        
        # Risk methods
        "var", "value at risk", "cvar", "expected shortfall",
        "monte carlo", "stress testing", "backtesting",
        "scenario analysis", "sensitivity analysis",
        
        # Quant tools
        "quantitative analysis", "quantitative modeling", "risk modeling",
        "portfolio optimization", "algorithmic trading", "quant trading",
        "derivatives pricing", "option pricing", "fixed income analytics"
    ]
    
    # AML/KYC keywords
    AML_KYC_KEYWORDS = [
        "aml", "anti-money laundering", "kyc", "know your customer",
        "transaction monitoring", "sanctions screening", "pep screening",
        "adverse media", "customer due diligence", "cdd", "edd",
        "enhanced due diligence", "suspicious activity", "sar",
        "ctr", "currency transaction report", "ofac", "fatf",
        "beneficial ownership", "ubo", "financial crime"
    ]
    
    # Financial tech stack indicators
    FINANCIAL_TECH_STACK = {
        "core_banking": ["temenos", "finastra", "fis", "fiserv", "jack henry",
                        "oracle flexcube", "infosys finacle", "mambu", "thought machine"],
        "trading": ["bloomberg terminal", "refinitiv", "factset", "murex",
                   "calypso", "fidessa", "ion", "broadridge"],
        "risk": ["moody's", "sas", "matlab", "numerix", "kamakura",
                "axiomsl", "oracle frm", "ibm algo"],
        "compliance": ["actimize", "nasdaq verafin", "fenergo", "accuity",
                      "lexisnexis", "refinitiv world-check", "dow jones"],
        "data": ["snowflake", "databricks", "palantir", "alteryx",
                "tableau", "power bi", "qlik", "looker"]
    }
    
    # Financial AI/ML roles
    FINANCIAL_AI_ROLES = [
        # Quant roles
        "quantitative analyst", "quant developer", "quantitative researcher",
        "quantitative trader", "algo trader", "systematic trader",
        
        # Risk roles
        "risk modeler", "credit risk analyst", "market risk analyst",
        "model risk analyst", "model validator", "risk data scientist",
        
        # Compliance roles
        "aml analyst", "kyc analyst", "compliance analyst",
        "financial crime analyst", "sanctions analyst",
        
        # Data & AI roles
        "financial data scientist", "financial ml engineer",
        "financial data engineer", "ai architect", "mlops engineer"
    ]
    
    def __init__(self):
        """Initialize financial scoring engine with specialized weights"""
        super().__init__()
        self.financial_weights = FinancialScoringWeights()
    
    def calculate_financial_ai_readiness(
        self,
        hunter_data: Optional[Dict[str, Any]] = None,
        web_scraping_data: Optional[Dict[str, Any]] = None,
        clearbit_data: Optional[Dict[str, Any]] = None,
        job_posting_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive AI readiness score for financial services companies
        
        Returns:
            Dictionary with detailed financial AI readiness assessment
        """
        
        component_scores = {}
        detailed_signals = {}
        confidence_factors = []
        
        # 1. Regulatory Compliance Readiness (20%)
        reg_score, reg_signals = self._calculate_regulatory_readiness(
            web_scraping_data, news_data, job_posting_data
        )
        component_scores["regulatory_compliance"] = reg_score
        detailed_signals["regulatory"] = reg_signals
        if reg_signals["data_sources"] > 0:
            confidence_factors.append(0.9)
        
        # 2. Data Governance & Infrastructure (20%)
        data_score, data_signals = self._calculate_data_governance_score(
            web_scraping_data, job_posting_data, news_data
        )
        component_scores["data_governance"] = data_score
        detailed_signals["data_governance"] = data_signals
        if data_signals["signals_found"] > 0:
            confidence_factors.append(0.85)
        
        # 3. Quantitative & Risk Capabilities (15%)
        quant_score, quant_signals = self._calculate_quant_capabilities(
            job_posting_data, web_scraping_data
        )
        component_scores["quant_risk_capabilities"] = quant_score
        detailed_signals["quant_risk"] = quant_signals
        if quant_signals["total_signals"] > 0:
            confidence_factors.append(0.8)
        
        # 4. AML/KYC & Financial Crime (15%)
        aml_score, aml_signals = self._calculate_aml_kyc_readiness(
            web_scraping_data, job_posting_data, news_data
        )
        component_scores["aml_kyc_capabilities"] = aml_score
        detailed_signals["aml_kyc"] = aml_signals
        if aml_signals["capabilities_found"] > 0:
            confidence_factors.append(0.75)
        
        # 5. Technology Modernization (15%)
        tech_score, tech_signals = self._calculate_tech_modernization(
            web_scraping_data, hunter_data, clearbit_data
        )
        component_scores["tech_modernization"] = tech_score
        detailed_signals["technology"] = tech_signals
        if len(tech_signals.get("modern_systems", [])) > 0:
            confidence_factors.append(0.8)
        
        # 6. AI/ML Team & Maturity (15%)
        ai_score, ai_signals = self._calculate_ai_ml_maturity(
            job_posting_data, web_scraping_data, news_data
        )
        component_scores["ai_ml_maturity"] = ai_score
        detailed_signals["ai_maturity"] = ai_signals
        if ai_signals["ai_initiatives"] > 0:
            confidence_factors.append(0.85)
        
        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(component_scores)
        
        # Determine readiness category
        readiness_category = self._get_financial_readiness_category(overall_score)
        
        # Calculate confidence
        confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.3
        
        # Generate financial-specific insights
        insights = self._generate_financial_insights(
            component_scores, detailed_signals, overall_score
        )
        
        # Generate recommendations
        recommendations = self._generate_financial_recommendations(
            component_scores, detailed_signals, readiness_category
        )
        
        return {
            "overall_score": overall_score,
            "readiness_category": readiness_category,
            "confidence": round(confidence, 2),
            "component_scores": component_scores,
            "detailed_signals": detailed_signals,
            "key_strengths": insights["strengths"],
            "improvement_areas": insights["weaknesses"],
            "financial_insights": insights["financial_specific"],
            "recommendations": recommendations,
            "scoring_methodology": "Financial Services Optimized"
        }
    
    def _calculate_regulatory_readiness(
        self, web_data: Optional[Dict], news_data: Optional[Dict], 
        job_data: Optional[Dict]
    ) -> tuple[int, Dict]:
        """Calculate regulatory compliance readiness score"""
        
        score = 0
        signals = {
            "regulations_mentioned": [],
            "compliance_roles": [],
            "governance_indicators": [],
            "data_sources": 0
        }
        
        # Check web scraping data
        if web_data:
            text = web_data.get("full_text", "").lower()
            for keyword in self.REGULATORY_KEYWORDS:
                if keyword in text:
                    signals["regulations_mentioned"].append(keyword)
            
            # Look for governance structures
            if any(term in text for term in ["chief risk officer", "cro", "chief compliance"]):
                signals["governance_indicators"].append("C-level risk/compliance leadership")
                score += 15
            
            if any(term in text for term in ["model risk management", "model validation"]):
                signals["governance_indicators"].append("Model risk framework")
                score += 20
            
            if signals["regulations_mentioned"]:
                score += min(len(signals["regulations_mentioned"]) * 5, 30)
            
            signals["data_sources"] += 1
        
        # Check job postings
        if job_data:
            for job in job_data.get("recent_job_titles", []):
                job_title = job.get("title", "").lower()
                if any(role in job_title for role in ["compliance", "risk", "regulatory", "audit"]):
                    signals["compliance_roles"].append(job_title)
            
            if signals["compliance_roles"]:
                score += min(len(signals["compliance_roles"]) * 5, 25)
            
            signals["data_sources"] += 1
        
        # Check news
        if news_data:
            for article in news_data.get("articles", [])[:5]:
                if any(reg in article.get("title", "").lower() or 
                      article.get("description", "").lower() 
                      for reg in ["compliance", "regulatory", "audit", "governance"]):
                    score += 5
            
            signals["data_sources"] += 1
        
        # Default score if no data
        if signals["data_sources"] == 0:
            score = 35  # Assume basic compliance
        
        return min(score, 100), signals
    
    def _calculate_data_governance_score(
        self, web_data: Optional[Dict], job_data: Optional[Dict], 
        news_data: Optional[Dict]
    ) -> tuple[int, Dict]:
        """Calculate data governance and infrastructure score"""
        
        score = 0
        signals = {
            "data_capabilities": [],
            "data_roles": [],
            "infrastructure": [],
            "signals_found": 0
        }
        
        if web_data:
            text = web_data.get("full_text", "").lower()
            
            # Check for data governance mentions
            for keyword in self.DATA_GOVERNANCE_KEYWORDS:
                if keyword in text:
                    signals["data_capabilities"].append(keyword)
                    signals["signals_found"] += 1
            
            # Check for cloud infrastructure
            if any(cloud in text for cloud in ["aws", "azure", "gcp", "google cloud"]):
                signals["infrastructure"].append("Cloud infrastructure")
                score += 15
            
            # Check for data platforms
            if any(platform in text for platform in ["snowflake", "databricks", "palantir"]):
                signals["infrastructure"].append("Modern data platform")
                score += 20
            
            if signals["data_capabilities"]:
                score += min(len(signals["data_capabilities"]) * 4, 40)
        
        if job_data:
            for job in job_data.get("recent_job_titles", []):
                job_title = job.get("title", "").lower()
                if any(role in job_title for role in ["data", "database", "etl", "analytics"]):
                    signals["data_roles"].append(job_title)
                    signals["signals_found"] += 1
            
            if signals["data_roles"]:
                score += min(len(signals["data_roles"]) * 5, 25)
        
        # Default if no data
        if signals["signals_found"] == 0:
            score = 30
        
        return min(score, 100), signals
    
    def _calculate_quant_capabilities(
        self, job_data: Optional[Dict], web_data: Optional[Dict]
    ) -> tuple[int, Dict]:
        """Calculate quantitative and risk modeling capabilities"""
        
        score = 0
        signals = {
            "quant_roles": [],
            "risk_capabilities": [],
            "quant_tools": [],
            "total_signals": 0
        }
        
        if job_data:
            # Check for quant roles
            for job in job_data.get("recent_job_titles", []):
                job_title = job.get("title", "").lower()
                for role in self.FINANCIAL_AI_ROLES:
                    if role in job_title:
                        signals["quant_roles"].append(job_title)
                        signals["total_signals"] += 1
                        break
            
            if signals["quant_roles"]:
                score += min(len(signals["quant_roles"]) * 10, 40)
            
            # Check for quant tools in job descriptions
            tech_stack = job_data.get("tech_stack_signals", [])
            quant_tools = ["python", "r", "matlab", "c++", "java", "scala"]
            for tool in quant_tools:
                if any(tool in str(k).lower() for k in tech_stack):
                    signals["quant_tools"].append(tool)
                    signals["total_signals"] += 1
            
            if signals["quant_tools"]:
                score += min(len(signals["quant_tools"]) * 5, 20)
        
        if web_data:
            text = web_data.get("full_text", "").lower()
            
            # Check for risk capabilities
            for keyword in self.QUANT_RISK_KEYWORDS:
                if keyword in text:
                    signals["risk_capabilities"].append(keyword)
                    signals["total_signals"] += 1
            
            if signals["risk_capabilities"]:
                score += min(len(signals["risk_capabilities"]) * 3, 40)
        
        # Default score
        if signals["total_signals"] == 0:
            score = 25
        
        return min(score, 100), signals
    
    def _calculate_aml_kyc_readiness(
        self, web_data: Optional[Dict], job_data: Optional[Dict], 
        news_data: Optional[Dict]
    ) -> tuple[int, Dict]:
        """Calculate AML/KYC and financial crime capabilities"""
        
        score = 0
        signals = {
            "aml_capabilities": [],
            "compliance_systems": [],
            "aml_roles": [],
            "capabilities_found": 0
        }
        
        if web_data:
            text = web_data.get("full_text", "").lower()
            
            # Check for AML/KYC mentions
            for keyword in self.AML_KYC_KEYWORDS:
                if keyword in text:
                    signals["aml_capabilities"].append(keyword)
                    signals["capabilities_found"] += 1
            
            # Check for compliance systems
            for vendor in self.FINANCIAL_TECH_STACK["compliance"]:
                if vendor.lower() in text:
                    signals["compliance_systems"].append(vendor)
                    score += 15
            
            if signals["aml_capabilities"]:
                score += min(len(signals["aml_capabilities"]) * 3, 40)
        
        if job_data:
            for job in job_data.get("recent_job_titles", []):
                job_title = job.get("title", "").lower()
                if any(role in job_title for role in ["aml", "kyc", "financial crime", "sanctions"]):
                    signals["aml_roles"].append(job_title)
                    signals["capabilities_found"] += 1
            
            if signals["aml_roles"]:
                score += min(len(signals["aml_roles"]) * 10, 30)
        
        # Default score
        if signals["capabilities_found"] == 0:
            score = 30  # Assume basic AML/KYC
        
        return min(score, 100), signals
    
    def _calculate_tech_modernization(
        self, web_data: Optional[Dict], hunter_data: Optional[Dict], 
        clearbit_data: Optional[Dict]
    ) -> tuple[int, Dict]:
        """Calculate technology modernization score"""
        
        score = 0
        signals = {
            "modern_systems": [],
            "legacy_indicators": [],
            "api_capabilities": [],
            "cloud_adoption": False
        }
        
        if web_data:
            text = web_data.get("full_text", "").lower()
            
            # Check for modern core banking systems
            for system in self.FINANCIAL_TECH_STACK["core_banking"]:
                if system.lower() in text:
                    if system.lower() in ["mambu", "thought machine", "temenos"]:
                        signals["modern_systems"].append(f"Modern core: {system}")
                        score += 25
                    else:
                        signals["legacy_indicators"].append(f"Traditional core: {system}")
                        score += 10
            
            # Check for API and microservices
            if any(term in text for term in ["api", "microservices", "rest", "graphql"]):
                signals["api_capabilities"].append("API-first architecture")
                score += 20
            
            # Check for cloud
            if any(cloud in text for cloud in ["cloud", "aws", "azure", "gcp"]):
                signals["cloud_adoption"] = True
                score += 20
            
            # Check for real-time capabilities
            if any(term in text for term in ["real-time", "streaming", "kafka", "event-driven"]):
                signals["modern_systems"].append("Real-time processing")
                score += 15
        
        # Use tech stack from other sources
        if hunter_data and hunter_data.get("technologies"):
            tech_list = hunter_data["technologies"]
            modern_tech = ["kubernetes", "docker", "react", "node.js", "python"]
            for tech in modern_tech:
                if any(tech.lower() in t.lower() for t in tech_list):
                    signals["modern_systems"].append(tech)
                    score += 5
        
        # Default score
        if not signals["modern_systems"] and not signals["legacy_indicators"]:
            score = 40  # Assume some modernization
        
        return min(score, 100), signals
    
    def _calculate_ai_ml_maturity(
        self, job_data: Optional[Dict], web_data: Optional[Dict], 
        news_data: Optional[Dict]
    ) -> tuple[int, Dict]:
        """Calculate AI/ML team and initiative maturity"""
        
        score = 0
        signals = {
            "ai_roles": [],
            "ai_use_cases": [],
            "ai_governance": [],
            "ai_initiatives": 0
        }
        
        if job_data:
            # Count AI/ML roles
            ai_ml_jobs = job_data.get("ai_ml_jobs_count", 0)
            if ai_ml_jobs > 10:
                score += 30
                signals["ai_initiatives"] += ai_ml_jobs
            elif ai_ml_jobs > 5:
                score += 20
                signals["ai_initiatives"] += ai_ml_jobs
            elif ai_ml_jobs > 0:
                score += 10
                signals["ai_initiatives"] += ai_ml_jobs
            
            # Check for specific AI roles
            for job in job_data.get("recent_job_titles", [])[:10]:
                job_title = job.get("title", "").lower()
                if any(role in job_title for role in ["data scientist", "ml engineer", "ai"]):
                    signals["ai_roles"].append(job_title)
        
        if web_data:
            text = web_data.get("full_text", "").lower()
            
            # Check for AI use cases
            ai_use_cases = [
                "fraud detection", "credit scoring", "robo-advisor",
                "chatbot", "customer service ai", "algorithmic trading",
                "risk modeling", "document processing", "kyc automation"
            ]
            for use_case in ai_use_cases:
                if use_case in text:
                    signals["ai_use_cases"].append(use_case)
                    score += 5
            
            # Check for AI governance
            if any(term in text for term in ["ai governance", "ai ethics", "responsible ai"]):
                signals["ai_governance"].append("AI governance framework")
                score += 15
            
            if "ai committee" in text or "ai steering" in text:
                signals["ai_governance"].append("AI committee")
                score += 10
        
        if news_data:
            # Check recent AI initiatives in news
            for article in news_data.get("articles", [])[:5]:
                if any(term in article.get("title", "").lower() 
                      for term in ["ai", "artificial intelligence", "machine learning"]):
                    signals["ai_initiatives"] += 1
                    score += 3
        
        # Default score
        if signals["ai_initiatives"] == 0:
            score = 20
        
        return min(score, 100), signals
    
    def _calculate_weighted_score(self, component_scores: Dict[str, int]) -> int:
        """Calculate weighted overall score using financial weights"""
        
        weights = self.financial_weights
        weighted_sum = (
            component_scores.get("regulatory_compliance", 0) * weights.regulatory_compliance +
            component_scores.get("data_governance", 0) * weights.data_governance +
            component_scores.get("quant_risk_capabilities", 0) * weights.quant_risk_capabilities +
            component_scores.get("aml_kyc_capabilities", 0) * weights.aml_kyc_capabilities +
            component_scores.get("tech_modernization", 0) * weights.tech_modernization +
            component_scores.get("ai_ml_maturity", 0) * weights.ai_ml_maturity
        )
        
        return round(weighted_sum)
    
    def _get_financial_readiness_category(self, score: int) -> str:
        """Get financial services specific readiness category"""
        
        if score >= 80:
            return "AI Leader - Ready for Advanced Use Cases"
        elif score >= 65:
            return "AI Ready - Strong Foundation"
        elif score >= 50:
            return "AI Exploring - Building Capabilities"
        elif score >= 35:
            return "AI Aware - Early Stage"
        else:
            return "AI Nascent - Foundation Needed"
    
    def _generate_financial_insights(
        self, scores: Dict, signals: Dict, overall_score: int
    ) -> Dict[str, List[str]]:
        """Generate financial services specific insights"""
        
        strengths = []
        weaknesses = []
        financial_specific = []
        
        # Analyze strengths
        if scores.get("regulatory_compliance", 0) > 70:
            strengths.append("Strong regulatory compliance framework")
            financial_specific.append("Well-positioned for AI governance requirements")
        
        if scores.get("data_governance", 0) > 70:
            strengths.append("Mature data governance capabilities")
            financial_specific.append("Data foundation ready for AI/ML modeling")
        
        if scores.get("quant_risk_capabilities", 0) > 60:
            strengths.append("Strong quantitative and risk modeling team")
            financial_specific.append("Existing quant capabilities can accelerate AI adoption")
        
        if scores.get("aml_kyc_capabilities", 0) > 60:
            strengths.append("Established AML/KYC processes")
            financial_specific.append("Ready for AI-enhanced financial crime detection")
        
        # Analyze weaknesses
        if scores.get("tech_modernization", 0) < 50:
            weaknesses.append("Legacy technology infrastructure")
            financial_specific.append("Core system modernization needed for real-time AI")
        
        if scores.get("ai_ml_maturity", 0) < 40:
            weaknesses.append("Limited AI/ML expertise")
            financial_specific.append("Need to build AI talent and governance structure")
        
        if scores.get("data_governance", 0) < 50:
            weaknesses.append("Data governance gaps")
            financial_specific.append("Data quality issues may impede AI model performance")
        
        # Add specific insights based on signals
        if signals.get("regulatory", {}).get("governance_indicators"):
            financial_specific.append("Model risk management framework detected")
        
        if signals.get("technology", {}).get("cloud_adoption"):
            financial_specific.append("Cloud infrastructure enables scalable AI deployment")
        
        if signals.get("aml_kyc", {}).get("compliance_systems"):
            financial_specific.append(f"Existing systems: {', '.join(signals['aml_kyc']['compliance_systems'][:3])}")
        
        return {
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "financial_specific": financial_specific[:5]
        }
    
    def _generate_financial_recommendations(
        self, scores: Dict, signals: Dict, category: str
    ) -> List[str]:
        """Generate financial services specific recommendations"""
        
        recommendations = []
        
        # High readiness recommendations (score >= 65)
        if "AI Ready" in category or "AI Leader" in category:
            recommendations.append(
                "Ready for advanced AI use cases: real-time fraud detection, "
                "algorithmic trading, automated credit decisioning"
            )
            
            if scores.get("regulatory_compliance", 0) > 70:
                recommendations.append(
                    "Leverage strong compliance framework to pioneer RegTech AI solutions"
                )
            
            if scores.get("quant_risk_capabilities", 0) > 70:
                recommendations.append(
                    "Expand quant team capabilities to AI-driven portfolio optimization and risk modeling"
                )
            
            recommendations.append(
                "Consider ModelML's platform for enterprise-wide AI orchestration and governance"
            )
        
        # Medium readiness (35-64)
        elif "AI Exploring" in category or "AI Aware" in category:
            recommendations.append(
                "Focus on high-ROI AI use cases: customer service automation, "
                "regulatory reporting, basic fraud detection"
            )
            
            if scores.get("data_governance", 0) < 50:
                recommendations.append(
                    "Prioritize data governance foundation: implement MDM, "
                    "establish data quality metrics, create data catalog"
                )
            
            if scores.get("tech_modernization", 0) < 50:
                recommendations.append(
                    "Modernize core infrastructure: adopt cloud, implement APIs, "
                    "move to microservices architecture"
                )
            
            if scores.get("ai_ml_maturity", 0) < 40:
                recommendations.append(
                    "Build AI capabilities: hire data scientists, establish AI CoE, "
                    "create governance framework"
                )
            
            recommendations.append(
                "Start with ModelML's pre-built financial AI models for quick wins"
            )
        
        # Low readiness (< 35)
        else:
            recommendations.append(
                "Begin with foundational improvements: data quality, "
                "regulatory compliance automation, basic RPA"
            )
            
            recommendations.append(
                "Focus on data governance: establish single source of truth, "
                "implement data quality controls"
            )
            
            recommendations.append(
                "Start small with rule-based automation before advancing to AI/ML"
            )
            
            recommendations.append(
                "Consider ModelML's consulting services for AI readiness assessment and roadmap"
            )
        
        # Add specific recommendations based on signals
        if not signals.get("regulatory", {}).get("governance_indicators"):
            recommendations.append(
                "Establish AI governance committee and model risk management framework"
            )
        
        if signals.get("aml_kyc", {}).get("capabilities_found", 0) > 5:
            recommendations.append(
                "Strong AML/KYC foundation - ideal for AI-powered transaction monitoring"
            )
        
        return recommendations[:5]
    
    def detect_financial_company(
        self, hunter_data: Optional[Dict] = None,
        clearbit_data: Optional[Dict] = None,
        company_name: str = ""
    ) -> bool:
        """
        Detect if a company is in financial services
        
        Returns:
            True if financial services company detected
        """
        
        # Check Hunter.io industry
        if hunter_data and hunter_data.get("company_industry"):
            industry = hunter_data["company_industry"].lower()
            financial_keywords = ["bank", "finance", "financial", "investment", 
                                 "asset", "insurance", "payment", "fintech"]
            if any(keyword in industry for keyword in financial_keywords):
                return True
        
        # Check Clearbit industry
        if clearbit_data and clearbit_data.get("industry"):
            industry = clearbit_data["industry"].lower()
            if any(keyword in industry for keyword in 
                  ["bank", "finance", "financial", "investment"]):
                return True
        
        # Check company name
        name_lower = company_name.lower()
        financial_indicators = ["bank", "capital", "financial", "investment",
                               "asset", "wealth", "securities", "insurance",
                               "jpmorgan", "goldman", "citi", "wells fargo",
                               "morgan stanley", "credit", "fidelity"]
        if any(indicator in name_lower for indicator in financial_indicators):
            return True
        
        return False