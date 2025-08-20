from typing import Dict, List

class RecommendationEngine:
    def generate_sales_approach(self, company_data: Dict, readiness_score: Dict) -> Dict:
        """
        Generate tailored sales recommendations based on AI readiness
        """
        score = readiness_score['total_score']
        level = readiness_score['readiness_level']
        
        # Get key decision makers
        decision_makers = self._identify_decision_makers(company_data)
        
        # Generate approach based on score tier
        if score >= 80:
            approach = self._high_readiness_approach(company_data)
        elif score >= 65:
            approach = self._medium_high_approach(company_data)
        elif score >= 50:
            approach = self._medium_approach(company_data)
        else:
            approach = self._low_readiness_approach(company_data)
            
        return {
            'readiness_level': level,
            'decision_makers': decision_makers,
            'sales_approach': approach,
            'key_talking_points': self._generate_talking_points(company_data, score),
            'potential_objections': self._identify_objections(score),
            'next_steps': self._recommend_next_steps(score)
        }
    
    def _identify_decision_makers(self, company_data: Dict) -> List[Dict]:
        """
        Identify key decision makers for AI initiatives
        """
        company_name = company_data.get('company_info', {}).get('name', 'Company')
        
        # Mock decision makers based on company
        if 'JPMorgan' in company_name:
            return [
                {
                    'name': 'Lori Beer',
                    'title': 'Global Chief Information Officer',
                    'relevance': 'Oversees all technology initiatives',
                    'approach': 'Focus on enterprise-scale AI deployment'
                },
                {
                    'name': 'Marco Pistoia',
                    'title': 'Head of Applied Research & Engineering',
                    'relevance': 'Leads AI/ML research initiatives',
                    'approach': 'Emphasize cutting-edge AI capabilities'
                }
            ]
        elif 'Goldman' in company_name:
            return [
                {
                    'name': 'Marco Argenti',
                    'title': 'Chief Information Officer',
                    'relevance': 'Drives digital transformation',
                    'approach': 'Highlight ROI and efficiency gains'
                },
                {
                    'name': 'George Lee',
                    'title': 'Co-Chief Information Officer',
                    'relevance': 'Focus on trading technology',
                    'approach': 'Emphasize real-time AI applications'
                }
            ]
        elif 'BlackRock' in company_name:
            return [
                {
                    'name': 'Sudhir Nair',
                    'title': 'Global Head of Aladdin',
                    'relevance': 'Oversees Aladdin platform',
                    'approach': 'Focus on AI integration with Aladdin'
                },
                {
                    'name': 'Rachel Lord',
                    'title': 'Head of International',
                    'relevance': 'Strategic technology decisions',
                    'approach': 'Emphasize global scalability'
                }
            ]
        else:
            return [
                {
                    'name': 'Chief Technology Officer',
                    'title': 'CTO',
                    'relevance': 'Technology strategy',
                    'approach': 'Focus on technical capabilities'
                },
                {
                    'name': 'Chief Data Officer',
                    'title': 'CDO',
                    'relevance': 'Data and AI strategy',
                    'approach': 'Emphasize data utilization'
                }
            ]
    
    def _high_readiness_approach(self, company_data: Dict) -> Dict:
        """Approach for highly AI-ready companies (80+)"""
        return {
            'strategy': 'Advanced Partnership',
            'messaging': 'Position ModelML as the next evolution in their AI journey',
            'focus_areas': [
                'Enterprise-scale AI deployment',
                'Advanced model optimization',
                'Cutting-edge capabilities beyond current tools',
                'Competitive advantage through AI'
            ],
            'urgency': 'High - They are actively investing in AI',
            'competitive_positioning': 'Show how ModelML surpasses their current solutions'
        }
    
    def _medium_high_approach(self, company_data: Dict) -> Dict:
        """Approach for medium-high readiness (65-79)"""
        return {
            'strategy': 'Strategic Enablement',
            'messaging': 'ModelML as the catalyst for AI transformation',
            'focus_areas': [
                'Accelerating existing AI initiatives',
                'Filling capability gaps',
                'Reducing time to production',
                'ROI and efficiency gains'
            ],
            'urgency': 'Medium-High - Building momentum',
            'competitive_positioning': 'Emphasize proven success with similar companies'
        }
    
    def _medium_approach(self, company_data: Dict) -> Dict:
        """Approach for medium readiness (50-64)"""
        return {
            'strategy': 'Education and Enablement',
            'messaging': 'ModelML as the foundation for AI success',
            'focus_areas': [
                'Low-risk pilot projects',
                'Quick wins and proof of concept',
                'Building AI capabilities',
                'Training and support'
            ],
            'urgency': 'Medium - Need to build confidence',
            'competitive_positioning': 'Focus on ease of adoption and support'
        }
    
    def _low_readiness_approach(self, company_data: Dict) -> Dict:
        """Approach for low readiness (<50)"""
        return {
            'strategy': 'Educational Nurturing',
            'messaging': 'Start the AI journey with a trusted partner',
            'focus_areas': [
                'AI education and awareness',
                'Industry use cases',
                'Small pilot opportunities',
                'Long-term vision building'
            ],
            'urgency': 'Low - Long-term relationship building',
            'competitive_positioning': 'Position as AI educator and partner'
        }
    
    def _generate_talking_points(self, company_data: Dict, score: float) -> List[str]:
        """Generate specific talking points based on company analysis"""
        points = []
        
        job_data = company_data.get('job_analysis', {})
        news_data = company_data.get('news_analysis', {})
        
        # Job posting insights
        ai_positions = job_data.get('ai_ml_positions', 0)
        if ai_positions > 20:
            points.append(f"You're hiring aggressively for AI talent ({ai_positions} open positions)")
        elif ai_positions > 5:
            points.append(f"Your {ai_positions} open AI/ML positions show commitment to AI")
        
        # Recent initiatives
        initiatives = news_data.get('recent_initiatives', [])
        if initiatives:
            latest = initiatives[0] if initiatives else None
            if latest:
                points.append(f"Your recent {latest.get('title', 'AI initiative')} aligns with ModelML")
        
        # Industry positioning
        if score >= 70:
            points.append("You're ahead of industry peers in AI adoption")
        elif score >= 50:
            points.append("Critical time to accelerate AI adoption to stay competitive")
        else:
            points.append("Opportunity to leapfrog competitors with right AI strategy")
            
        # Tech stack alignment
        website_data = company_data.get('website_analysis', {})
        tech_stack = website_data.get('tech_stack_visible', [])
        if 'Python' in tech_stack or 'python' in str(tech_stack).lower():
            points.append("ModelML integrates seamlessly with your Python infrastructure")
            
        return points
    
    def _identify_objections(self, score: float) -> List[Dict]:
        """Identify likely objections based on readiness level"""
        objections = []
        
        if score >= 80:
            objections.append({
                'objection': 'We already have AI capabilities',
                'response': 'ModelML enhances and scales existing capabilities'
            })
            objections.append({
                'objection': 'Integration complexity',
                'response': 'Seamless integration with proven enterprise deployment'
            })
        elif score >= 50:
            objections.append({
                'objection': 'ROI uncertainty',
                'response': 'Proven ROI with similar financial institutions'
            })
            objections.append({
                'objection': 'Resource constraints',
                'response': 'ModelML reduces resource needs through automation'
            })
        else:
            objections.append({
                'objection': 'Not ready for AI',
                'response': 'Start small with pilot projects and grow'
            })
            objections.append({
                'objection': 'Lack of AI expertise',
                'response': 'Full training and support included'
            })
            
        return objections
    
    def _recommend_next_steps(self, score: float) -> List[str]:
        """Recommend immediate next steps for sales team"""
        if score >= 80:
            return [
                "Schedule executive briefing within 1 week",
                "Prepare custom demo with their use cases",
                "Identify current AI pain points",
                "Propose pilot project for immediate value"
            ]
        elif score >= 65:
            return [
                "Schedule technical deep-dive session",
                "Share relevant case studies",
                "Identify champion within organization",
                "Propose proof of concept"
            ]
        elif score >= 50:
            return [
                "Send educational materials",
                "Schedule discovery call",
                "Identify specific use cases",
                "Offer workshop or training session"
            ]
        else:
            return [
                "Add to nurture campaign",
                "Share industry AI trends report",
                "Schedule quarterly check-in",
                "Invite to ModelML webinars"
            ]