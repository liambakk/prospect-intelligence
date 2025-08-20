"""
Comprehensive tests for Financial AI Readiness Scoring Engine
Tests financial-specific scoring criteria and recommendations
"""

import pytest
import asyncio
from typing import Dict, Any
from src.services.financial_scoring_engine import FinancialAIReadinessScoringEngine
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestFinancialScoring:
    """Test suite for financial services AI readiness scoring"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = FinancialAIReadinessScoringEngine()
    
    def test_detect_financial_company(self):
        """Test financial company detection"""
        print("\n=== Testing Financial Company Detection ===")
        
        # Test with Hunter.io data
        hunter_data = {"company_industry": "Banking and Financial Services"}
        assert self.engine.detect_financial_company(hunter_data=hunter_data) == True
        print("✓ Detected banking from Hunter.io data")
        
        # Test with Clearbit data
        clearbit_data = {"industry": "Investment Management"}
        assert self.engine.detect_financial_company(clearbit_data=clearbit_data) == True
        print("✓ Detected investment management from Clearbit data")
        
        # Test with company name
        assert self.engine.detect_financial_company(company_name="JPMorgan Chase") == True
        assert self.engine.detect_financial_company(company_name="Goldman Sachs") == True
        assert self.engine.detect_financial_company(company_name="Wells Fargo") == True
        assert self.engine.detect_financial_company(company_name="Fidelity Investments") == True
        print("✓ Detected financial companies from names")
        
        # Test non-financial companies
        assert self.engine.detect_financial_company(company_name="Google") == False
        assert self.engine.detect_financial_company(company_name="Tesla") == False
        print("✓ Correctly identified non-financial companies")
    
    def test_regulatory_compliance_scoring(self):
        """Test regulatory compliance readiness scoring"""
        print("\n=== Testing Regulatory Compliance Scoring ===")
        
        # Test with strong regulatory signals
        web_data = {
            "full_text": "Chief Risk Officer leads our Basel III compliance and model risk management framework. We implement SR 11-7 model validation and maintain regulatory reporting automation."
        }
        
        job_data = {
            "recent_job_titles": [
                {"title": "Compliance Manager"},
                {"title": "Risk Analyst"},
                {"title": "Regulatory Reporting Specialist"}
            ]
        }
        
        score, signals = self.engine._calculate_regulatory_readiness(web_data, None, job_data)
        
        assert score > 60, f"Expected score > 60, got {score}"
        assert "model risk management" in signals["regulations_mentioned"]
        assert "C-level risk/compliance leadership" in signals["governance_indicators"]
        assert len(signals["compliance_roles"]) == 3
        print(f"✓ Strong regulatory compliance: Score={score}, Signals={signals['data_sources']} sources")
        
        # Test with minimal regulatory signals
        minimal_web = {"full_text": "We follow industry standards"}
        score_minimal, _ = self.engine._calculate_regulatory_readiness(minimal_web, None, None)
        
        assert score_minimal < score, "Minimal signals should score lower"
        print(f"✓ Minimal regulatory signals: Score={score_minimal}")
    
    def test_data_governance_scoring(self):
        """Test data governance and infrastructure scoring"""
        print("\n=== Testing Data Governance Scoring ===")
        
        web_data = {
            "full_text": "Our data lake on AWS powers real-time analytics. We use Snowflake for data warehousing and maintain strict data governance with MDM and data lineage tracking."
        }
        
        job_data = {
            "recent_job_titles": [
                {"title": "Data Engineer"},
                {"title": "Analytics Manager"},
                {"title": "Database Administrator"}
            ]
        }
        
        score, signals = self.engine._calculate_data_governance_score(web_data, job_data, None)
        
        assert score > 50, f"Expected score > 50, got {score}"
        assert "Cloud infrastructure" in signals["infrastructure"]
        assert "Modern data platform" in signals["infrastructure"]
        assert len(signals["data_roles"]) == 3
        print(f"✓ Strong data governance: Score={score}, Found {signals['signals_found']} signals")
    
    def test_quant_capabilities_scoring(self):
        """Test quantitative and risk modeling capabilities"""
        print("\n=== Testing Quantitative Capabilities Scoring ===")
        
        job_data = {
            "recent_job_titles": [
                {"title": "Quantitative Analyst"},
                {"title": "Risk Modeler"},
                {"title": "Quantitative Researcher"}
            ],
            "tech_stack_signals": ["python", "matlab", "r", "c++"]
        }
        
        web_data = {
            "full_text": "Our team uses Monte Carlo simulations for VaR calculations and portfolio optimization with advanced derivatives pricing models."
        }
        
        score, signals = self.engine._calculate_quant_capabilities(job_data, web_data)
        
        assert score > 60, f"Expected score > 60, got {score}"
        assert len(signals["quant_roles"]) == 3
        assert "python" in signals["quant_tools"]
        assert any("monte carlo" in cap for cap in signals["risk_capabilities"])
        print(f"✓ Strong quant capabilities: Score={score}, {signals['total_signals']} total signals")
    
    def test_aml_kyc_scoring(self):
        """Test AML/KYC and financial crime capabilities"""
        print("\n=== Testing AML/KYC Capabilities Scoring ===")
        
        web_data = {
            "full_text": "We use Actimize for transaction monitoring and sanctions screening. Our KYC processes include enhanced due diligence and continuous monitoring."
        }
        
        job_data = {
            "recent_job_titles": [
                {"title": "AML Analyst"},
                {"title": "KYC Specialist"},
                {"title": "Financial Crime Investigator"}
            ]
        }
        
        score, signals = self.engine._calculate_aml_kyc_readiness(web_data, job_data, None)
        
        assert score > 50, f"Expected score > 50, got {score}"
        assert "actimize" in signals["compliance_systems"]
        assert len(signals["aml_roles"]) == 3
        assert signals["capabilities_found"] > 0
        print(f"✓ Strong AML/KYC: Score={score}, {signals['capabilities_found']} capabilities found")
    
    def test_tech_modernization_scoring(self):
        """Test technology modernization scoring"""
        print("\n=== Testing Technology Modernization Scoring ===")
        
        web_data = {
            "full_text": "Our API-first microservices architecture runs on AWS cloud. We use Thought Machine for core banking with real-time streaming via Kafka."
        }
        
        hunter_data = {
            "technologies": ["kubernetes", "docker", "react", "node.js", "python"]
        }
        
        score, signals = self.engine._calculate_tech_modernization(web_data, hunter_data, None)
        
        assert score > 70, f"Expected score > 70, got {score}"
        assert signals["cloud_adoption"] == True
        assert "API-first architecture" in signals["api_capabilities"]
        assert any("thought machine" in sys.lower() for sys in signals["modern_systems"])
        print(f"✓ Modern tech stack: Score={score}, {len(signals['modern_systems'])} modern systems")
    
    def test_ai_ml_maturity_scoring(self):
        """Test AI/ML team and initiative maturity scoring"""
        print("\n=== Testing AI/ML Maturity Scoring ===")
        
        job_data = {
            "ai_ml_jobs_count": 12,
            "recent_job_titles": [
                {"title": "Data Scientist"},
                {"title": "ML Engineer"},
                {"title": "AI Research Lead"}
            ]
        }
        
        web_data = {
            "full_text": "Our AI governance committee oversees fraud detection and credit scoring models. We follow responsible AI principles with explainable models."
        }
        
        news_data = {
            "articles": [
                {"title": "Company launches AI-powered trading platform"},
                {"title": "New machine learning models improve risk assessment"},
                {"title": "AI chatbot reduces customer service time by 50%"}
            ]
        }
        
        score, signals = self.engine._calculate_ai_ml_maturity(job_data, web_data, news_data)
        
        assert score > 60, f"Expected score > 60, got {score}"
        assert signals["ai_initiatives"] > 10
        assert "AI governance framework" in signals["ai_governance"]
        assert "fraud detection" in signals["ai_use_cases"]
        print(f"✓ Strong AI maturity: Score={score}, {signals['ai_initiatives']} AI initiatives")
    
    def test_comprehensive_financial_scoring(self):
        """Test complete financial AI readiness scoring"""
        print("\n=== Testing Comprehensive Financial Scoring ===")
        
        # Prepare comprehensive test data
        hunter_data = {
            "company_industry": "Banking",
            "technologies": ["python", "kubernetes", "aws"]
        }
        
        web_data = {
            "full_text": """
            JPMorgan Chase leverages AI for fraud detection and algorithmic trading.
            Our Chief Risk Officer oversees model risk management under SR 11-7.
            We use Snowflake and AWS for our data infrastructure.
            Our quantitative team uses Monte Carlo simulations for risk modeling.
            KYC processes are automated with Actimize.
            API-first architecture enables real-time processing.
            AI governance committee ensures responsible AI deployment.
            """
        }
        
        job_data = {
            "ai_ml_jobs_count": 8,
            "recent_job_titles": [
                {"title": "Quantitative Analyst"},
                {"title": "ML Engineer"},
                {"title": "Risk Modeler"},
                {"title": "Compliance Manager"}
            ],
            "tech_stack_signals": ["python", "tensorflow", "spark"]
        }
        
        news_data = {
            "articles": [
                {"title": "JPMorgan invests in AI for trading"},
                {"title": "Bank launches new fraud detection system", "description": "Using machine learning"}
            ]
        }
        
        # Run comprehensive scoring
        result = self.engine.calculate_financial_ai_readiness(
            hunter_data=hunter_data,
            web_scraping_data=web_data,
            job_posting_data=job_data,
            news_data=news_data
        )
        
        # Verify results
        assert result["overall_score"] > 40, f"Expected score > 40, got {result['overall_score']}"
        assert result["confidence"] > 0.5, f"Expected confidence > 0.5, got {result['confidence']}"
        assert "component_scores" in result
        assert "financial_insights" in result
        assert "recommendations" in result
        assert result["scoring_methodology"] == "Financial Services Optimized"
        
        print(f"\n✓ Comprehensive Financial Scoring Results:")
        print(f"  Overall Score: {result['overall_score']}/100")
        print(f"  Category: {result['readiness_category']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"\n  Component Scores:")
        for component, score in result['component_scores'].items():
            print(f"    - {component}: {score}/100")
        
        # Test that all components are scored
        expected_components = [
            "regulatory_compliance",
            "data_governance",
            "quant_risk_capabilities",
            "aml_kyc_capabilities",
            "tech_modernization",
            "ai_ml_maturity"
        ]
        for component in expected_components:
            assert component in result["component_scores"], f"Missing component: {component}"
            print(f"  ✓ {component} scored: {result['component_scores'][component]}")
    
    def test_financial_recommendations(self):
        """Test financial-specific recommendations generation"""
        print("\n=== Testing Financial Recommendations ===")
        
        # Test high readiness recommendations
        high_scores = {
            "regulatory_compliance": 80,
            "data_governance": 75,
            "quant_risk_capabilities": 85,
            "aml_kyc_capabilities": 70,
            "tech_modernization": 65,
            "ai_ml_maturity": 70
        }
        
        recommendations = self.engine._generate_financial_recommendations(
            high_scores, {}, "AI Ready - Strong Foundation"
        )
        
        assert len(recommendations) > 0
        assert any("ModelML" in rec for rec in recommendations)
        assert any("advanced AI use cases" in rec for rec in recommendations)
        print(f"✓ High readiness: {len(recommendations)} recommendations generated")
        
        # Test low readiness recommendations
        low_scores = {
            "regulatory_compliance": 30,
            "data_governance": 25,
            "quant_risk_capabilities": 20,
            "aml_kyc_capabilities": 30,
            "tech_modernization": 25,
            "ai_ml_maturity": 15
        }
        
        low_recommendations = self.engine._generate_financial_recommendations(
            low_scores, {}, "AI Nascent - Foundation Needed"
        )
        
        assert len(low_recommendations) > 0
        assert any("foundation" in rec.lower() for rec in low_recommendations)
        assert any("data governance" in rec.lower() for rec in low_recommendations)
        print(f"✓ Low readiness: {len(low_recommendations)} recommendations generated")
    
    def test_financial_sector_benchmarks(self):
        """Test financial sector-specific benchmarks"""
        print("\n=== Testing Financial Sector Benchmarks ===")
        
        # Verify sector scores are defined
        assert "fintech" in self.engine.FINANCIAL_SECTOR_SCORES
        assert "hedge fund" in self.engine.FINANCIAL_SECTOR_SCORES
        assert "retail banking" in self.engine.FINANCIAL_SECTOR_SCORES
        assert "insurance" in self.engine.FINANCIAL_SECTOR_SCORES
        
        # Verify scoring hierarchy (fintech should score higher than community bank)
        assert self.engine.FINANCIAL_SECTOR_SCORES["fintech"] > self.engine.FINANCIAL_SECTOR_SCORES["community bank"]
        assert self.engine.FINANCIAL_SECTOR_SCORES["investment banking"] > self.engine.FINANCIAL_SECTOR_SCORES["regional bank"]
        
        print(f"✓ Sector benchmarks verified: {len(self.engine.FINANCIAL_SECTOR_SCORES)} sectors defined")
        print(f"  Highest: Fintech ({self.engine.FINANCIAL_SECTOR_SCORES['fintech']})")
        print(f"  Lowest: Credit Union ({self.engine.FINANCIAL_SECTOR_SCORES['credit union']})")
    
    def test_financial_keywords_coverage(self):
        """Test coverage of financial-specific keywords"""
        print("\n=== Testing Financial Keywords Coverage ===")
        
        # Test regulatory keywords
        assert len(self.engine.REGULATORY_KEYWORDS) > 10
        assert "basel iii" in self.engine.REGULATORY_KEYWORDS
        assert "sr 11-7" in self.engine.REGULATORY_KEYWORDS
        print(f"✓ {len(self.engine.REGULATORY_KEYWORDS)} regulatory keywords defined")
        
        # Test data governance keywords
        assert len(self.engine.DATA_GOVERNANCE_KEYWORDS) > 10
        assert "data lineage" in self.engine.DATA_GOVERNANCE_KEYWORDS
        print(f"✓ {len(self.engine.DATA_GOVERNANCE_KEYWORDS)} data governance keywords defined")
        
        # Test quant/risk keywords
        assert len(self.engine.QUANT_RISK_KEYWORDS) > 15
        assert "monte carlo" in self.engine.QUANT_RISK_KEYWORDS
        print(f"✓ {len(self.engine.QUANT_RISK_KEYWORDS)} quant/risk keywords defined")
        
        # Test AML/KYC keywords
        assert len(self.engine.AML_KYC_KEYWORDS) > 15
        assert "enhanced due diligence" in self.engine.AML_KYC_KEYWORDS
        print(f"✓ {len(self.engine.AML_KYC_KEYWORDS)} AML/KYC keywords defined")
        
        # Test financial tech stack
        assert "core_banking" in self.engine.FINANCIAL_TECH_STACK
        assert "temenos" in self.engine.FINANCIAL_TECH_STACK["core_banking"]
        assert "bloomberg terminal" in self.engine.FINANCIAL_TECH_STACK["trading"]
        print(f"✓ {len(self.engine.FINANCIAL_TECH_STACK)} tech stack categories defined")


def run_financial_tests():
    """Run all financial scoring tests"""
    print("\n" + "="*60)
    print("FINANCIAL AI READINESS SCORING ENGINE TESTS")
    print("="*60)
    
    test_suite = TestFinancialScoring()
    test_suite.setup_method()
    
    # Run all tests
    test_methods = [
        test_suite.test_detect_financial_company,
        test_suite.test_regulatory_compliance_scoring,
        test_suite.test_data_governance_scoring,
        test_suite.test_quant_capabilities_scoring,
        test_suite.test_aml_kyc_scoring,
        test_suite.test_tech_modernization_scoring,
        test_suite.test_ai_ml_maturity_scoring,
        test_suite.test_comprehensive_financial_scoring,
        test_suite.test_financial_recommendations,
        test_suite.test_financial_sector_benchmarks,
        test_suite.test_financial_keywords_coverage
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ Test failed: {test_method.__name__}")
            print(f"   Error: {str(e)}")
    
    # Summary
    print("\n" + "="*60)
    print("FINANCIAL SCORING TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL FINANCIAL SCORING TESTS PASSED!")
    else:
        print(f"\n⚠️ {failed} tests failed - review implementation")
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_financial_tests()
    
    # Exit with appropriate code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)