"""
Decision Maker Identification Service
Identifies key stakeholders for ModelML sales outreach
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class DecisionMakerService:
    """
    Service to identify and profile key decision makers at target companies
    Focuses on AI/ML adoption decision makers in financial services
    """
    
    # Key roles to target for ModelML sales
    PRIORITY_TITLES = {
        # C-Suite and Executive
        "ceo": {"priority": 1, "role": "Executive Sponsor", "approach": "Vision and strategic value"},
        "cto": {"priority": 1, "role": "Technology Leader", "approach": "Technical capabilities and innovation"},
        "cio": {"priority": 1, "role": "IT Strategy", "approach": "Infrastructure and integration"},
        "cdo": {"priority": 1, "role": "Data Strategy", "approach": "Data value and insights"},
        "chief data officer": {"priority": 1, "role": "Data Strategy", "approach": "Data governance and analytics"},
        "chief technology officer": {"priority": 1, "role": "Technology Leader", "approach": "Platform capabilities"},
        "chief information officer": {"priority": 1, "role": "IT Strategy", "approach": "Enterprise integration"},
        "chief analytics officer": {"priority": 1, "role": "Analytics Leader", "approach": "Analytical capabilities"},
        "chief ai officer": {"priority": 1, "role": "AI Strategy", "approach": "AI transformation roadmap"},
        "chief innovation officer": {"priority": 1, "role": "Innovation Leader", "approach": "Competitive advantage"},
        
        # VP Level
        "vp engineering": {"priority": 2, "role": "Engineering Leader", "approach": "Technical implementation"},
        "vp data": {"priority": 2, "role": "Data Leader", "approach": "Data platform capabilities"},
        "vp technology": {"priority": 2, "role": "Technology Leader", "approach": "Tech stack modernization"},
        "vp ai": {"priority": 2, "role": "AI Leader", "approach": "AI/ML use cases"},
        "vp machine learning": {"priority": 2, "role": "ML Leader", "approach": "ML operations and scale"},
        "vp analytics": {"priority": 2, "role": "Analytics Leader", "approach": "Business intelligence"},
        "vp innovation": {"priority": 2, "role": "Innovation Leader", "approach": "Emerging technologies"},
        "vp digital": {"priority": 2, "role": "Digital Leader", "approach": "Digital transformation"},
        "vp infrastructure": {"priority": 2, "role": "Infrastructure Leader", "approach": "Scalability and reliability"},
        
        # Director Level
        "director data science": {"priority": 3, "role": "Data Science Leader", "approach": "Model development and deployment"},
        "director engineering": {"priority": 3, "role": "Engineering Manager", "approach": "Implementation details"},
        "director ai": {"priority": 3, "role": "AI Manager", "approach": "AI project execution"},
        "director machine learning": {"priority": 3, "role": "ML Manager", "approach": "ML pipeline and operations"},
        "director analytics": {"priority": 3, "role": "Analytics Manager", "approach": "Analytics solutions"},
        "head of data": {"priority": 3, "role": "Data Head", "approach": "Data strategy execution"},
        "head of ai": {"priority": 3, "role": "AI Head", "approach": "AI initiatives"},
        "head of machine learning": {"priority": 3, "role": "ML Head", "approach": "ML platform needs"},
        "head of engineering": {"priority": 3, "role": "Engineering Head", "approach": "Technical requirements"},
        
        # Financial Services Specific
        "chief risk officer": {"priority": 2, "role": "Risk Leader", "approach": "Risk modeling and compliance"},
        "head of quantitative": {"priority": 2, "role": "Quant Leader", "approach": "Quantitative modeling capabilities"},
        "head of trading": {"priority": 2, "role": "Trading Leader", "approach": "Trading algorithms and automation"},
        "chief compliance officer": {"priority": 3, "role": "Compliance Leader", "approach": "Regulatory compliance features"},
        "head of investment": {"priority": 3, "role": "Investment Leader", "approach": "Investment analytics and insights"},
    }
    
    def __init__(self):
        """Initialize the decision maker service"""
        self.financial_keywords = [
            "risk", "trading", "investment", "compliance", "regulatory",
            "quant", "portfolio", "asset", "wealth", "banking", "financial"
        ]
    
    def identify_decision_makers(self, 
                                hunter_data: Optional[Dict[str, Any]] = None,
                                company_name: str = "",
                                is_financial: bool = False) -> List[Dict[str, Any]]:
        """
        Identify key decision makers from available data
        
        Args:
            hunter_data: Data from Hunter.io API
            company_name: Name of the company
            is_financial: Whether the company is in financial services
            
        Returns:
            List of decision makers with contact strategies
        """
        decision_makers = []
        
        # Extract contacts from Hunter.io data
        if hunter_data and hunter_data.get("contacts"):
            for contact in hunter_data["contacts"]:
                dm = self._process_contact(contact, is_financial)
                if dm:
                    decision_makers.append(dm)
        
        # If no specific contacts found, generate recommended targets
        if not decision_makers:
            decision_makers = self._generate_target_profiles(company_name, is_financial)
        
        # Sort by priority
        decision_makers.sort(key=lambda x: (x.get("priority", 999), x.get("confidence", 0)), reverse=False)
        
        return decision_makers[:5]  # Return top 5 decision makers
    
    def _process_contact(self, contact: Dict[str, Any], is_financial: bool) -> Optional[Dict[str, Any]]:
        """
        Process a contact from Hunter.io into a decision maker profile
        """
        title = contact.get("title", "").lower()
        if not title:
            return None
        
        # Check if title matches our priority roles
        matched_role = self._match_title(title)
        if not matched_role:
            return None
        
        # Build decision maker profile
        profile = {
            "name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip() or "Unknown",
            "title": contact.get("title", "Unknown"),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "linkedin": contact.get("linkedin", ""),
            "priority": matched_role["priority"],
            "role": matched_role["role"],
            "approach": self._customize_approach(matched_role["approach"], is_financial),
            "confidence": contact.get("confidence", 50),
            "seniority": contact.get("seniority", ""),
            "department": contact.get("department", ""),
            "talking_points": self._generate_talking_points(matched_role["role"], is_financial)
        }
        
        return profile
    
    def _match_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Match a job title to our priority roles
        """
        title_lower = title.lower()
        
        # Direct match
        for key, value in self.PRIORITY_TITLES.items():
            if key in title_lower:
                return value
        
        # Partial matches for common variations
        if "chief" in title_lower and "data" in title_lower:
            return self.PRIORITY_TITLES["cdo"]
        if "chief" in title_lower and ("tech" in title_lower or "technology" in title_lower):
            return self.PRIORITY_TITLES["cto"]
        if "vp" in title_lower and "data" in title_lower:
            return self.PRIORITY_TITLES["vp data"]
        if "director" in title_lower and ("ai" in title_lower or "artificial" in title_lower):
            return self.PRIORITY_TITLES["director ai"]
        if "head" in title_lower and "data" in title_lower:
            return self.PRIORITY_TITLES["head of data"]
        
        return None
    
    def _customize_approach(self, base_approach: str, is_financial: bool) -> str:
        """
        Customize the sales approach based on industry
        """
        if is_financial:
            return f"{base_approach} with focus on regulatory compliance and risk management"
        return base_approach
    
    def _generate_talking_points(self, role: str, is_financial: bool) -> List[str]:
        """
        Generate role-specific talking points for sales outreach
        """
        base_points = {
            "Executive Sponsor": [
                "Accelerate AI transformation across the organization",
                "Reduce time-to-market for AI initiatives by 70%",
                "Achieve competitive advantage through advanced AI capabilities"
            ],
            "Technology Leader": [
                "Unified AI platform reducing infrastructure complexity",
                "Seamless integration with existing tech stack",
                "Enterprise-grade scalability and security"
            ],
            "Data Strategy": [
                "Transform raw data into actionable AI insights",
                "Automated data pipeline for ML workflows",
                "Data governance and lineage tracking"
            ],
            "AI Strategy": [
                "End-to-end AI lifecycle management",
                "Pre-built models for common use cases",
                "MLOps best practices built-in"
            ],
            "Engineering Leader": [
                "Reduce AI development time from months to weeks",
                "Automated model deployment and monitoring",
                "Developer-friendly APIs and SDKs"
            ],
            "Analytics Leader": [
                "Advanced predictive analytics capabilities",
                "Real-time insights and decision support",
                "Self-service analytics for business users"
            ]
        }
        
        points = base_points.get(role, [
            "Streamline AI/ML operations",
            "Reduce development costs and time",
            "Scale AI initiatives across the organization"
        ])
        
        # Add financial-specific points if applicable
        if is_financial:
            financial_points = [
                "SOC 2 Type II certified, bank-grade security",
                "Compliance with financial regulations (GDPR, CCPA, etc.)",
                "Risk modeling and fraud detection capabilities",
                "Real-time transaction analysis and monitoring"
            ]
            points = points[:2] + financial_points[:2]
        
        return points
    
    def _generate_target_profiles(self, company_name: str, is_financial: bool) -> List[Dict[str, Any]]:
        """
        Generate recommended target profiles when no specific contacts are available
        """
        profiles = []
        
        # Select priority roles based on company type
        if is_financial:
            priority_roles = [
                ("Chief Data Officer", "cdo"),
                ("Chief Technology Officer", "cto"),
                ("VP of Data & Analytics", "vp data"),
                ("Chief Risk Officer", "chief risk officer"),
                ("Head of Quantitative Research", "head of quantitative")
            ]
        else:
            priority_roles = [
                ("Chief Technology Officer", "cto"),
                ("Chief Data Officer", "cdo"),
                ("VP of Engineering", "vp engineering"),
                ("VP of AI/ML", "vp ai"),
                ("Director of Data Science", "director data science")
            ]
        
        for title, key in priority_roles[:3]:
            role_info = self.PRIORITY_TITLES.get(key, {})
            profiles.append({
                "name": f"[Identify {title}]",
                "title": title,
                "email": "",
                "priority": role_info.get("priority", 3),
                "role": role_info.get("role", "Decision Maker"),
                "approach": self._customize_approach(
                    role_info.get("approach", "Focus on value proposition"),
                    is_financial
                ),
                "confidence": 0,
                "talking_points": self._generate_talking_points(
                    role_info.get("role", "Decision Maker"),
                    is_financial
                ),
                "research_needed": True,
                "suggested_research": [
                    f"Search LinkedIn for {title} at {company_name}",
                    f"Check {company_name} leadership page",
                    f"Use sales intelligence tools to identify {title}"
                ]
            })
        
        return profiles
    
    def generate_outreach_strategy(self, decision_makers: List[Dict[str, Any]], 
                                  ai_readiness_score: int,
                                  company_name: str) -> Dict[str, Any]:
        """
        Generate a comprehensive outreach strategy based on decision makers and company readiness
        """
        strategy = {
            "approach": self._determine_approach(ai_readiness_score),
            "messaging": self._create_messaging(ai_readiness_score),
            "sequence": [],
            "channels": [],
            "timeline": ""
        }
        
        # Determine outreach sequence
        if ai_readiness_score >= 70:
            strategy["approach"] = "Executive Fast-Track"
            strategy["timeline"] = "Aggressive (1-2 weeks)"
            strategy["channels"] = ["Direct executive outreach", "LinkedIn InMail", "Warm introduction"]
        elif ai_readiness_score >= 50:
            strategy["approach"] = "Technical Champion"
            strategy["timeline"] = "Standard (2-4 weeks)"
            strategy["channels"] = ["Email sequence", "LinkedIn engagement", "Technical webinar invite"]
        else:
            strategy["approach"] = "Education First"
            strategy["timeline"] = "Nurture (4-8 weeks)"
            strategy["channels"] = ["Educational content", "Industry reports", "Case studies"]
        
        # Create outreach sequence for each decision maker
        for dm in decision_makers[:3]:  # Focus on top 3
            sequence_item = {
                "target": dm.get("name", "Unknown"),
                "role": dm.get("role", ""),
                "week_1": f"Initial outreach: {dm.get('approach', '')}",
                "week_2": f"Follow up with: {', '.join(dm.get('talking_points', [])[:2])}",
                "week_3": "Share relevant case study or demo",
                "week_4": "Schedule discovery call"
            }
            strategy["sequence"].append(sequence_item)
        
        return strategy
    
    def _determine_approach(self, score: int) -> str:
        """Determine sales approach based on AI readiness"""
        if score >= 80:
            return "Immediate value demonstration - they're ready to buy"
        elif score >= 65:
            return "Proof of concept approach - show quick wins"
        elif score >= 50:
            return "Educational approach - build the business case"
        else:
            return "Long-term nurture - develop AI awareness"
    
    def _create_messaging(self, score: int) -> str:
        """Create appropriate messaging based on readiness"""
        if score >= 80:
            return "Your AI infrastructure is advanced. ModelML can help you scale 10x faster and reduce costs by 40%."
        elif score >= 65:
            return "You're on the AI journey. ModelML can accelerate your progress and avoid common pitfalls."
        elif score >= 50:
            return "Starting with AI? ModelML provides the complete platform to go from idea to production."
        else:
            return "Exploring AI possibilities? Learn how industry leaders are transforming with ModelML."