"""
Comprehensive test suite for AI Readiness Scoring Engine
Tests accuracy, edge cases, and weighted calculations
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.scoring_engine import AIReadinessScoringEngine, ScoringWeights
import json


def test_scoring_weights():
    """Test that weights sum to 1.0 (100%)"""
    print("\n1. Testing scoring weights...")
    
    weights = ScoringWeights()
    total = (weights.tech_hiring + weights.ai_mentions + 
             weights.company_size + weights.industry_adoption + 
             weights.tech_modernization)
    
    assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, should be 1.0"
    print(f"✓ Weights correctly sum to {total}")
    print(f"  - Tech Hiring: {weights.tech_hiring * 100}%")
    print(f"  - AI Mentions: {weights.ai_mentions * 100}%")
    print(f"  - Company Size: {weights.company_size * 100}%")
    print(f"  - Industry Adoption: {weights.industry_adoption * 100}%")
    print(f"  - Tech Modernization: {weights.tech_modernization * 100}%")


def test_perfect_company():
    """Test scoring with a perfect AI-ready company"""
    print("\n2. Testing perfect AI-ready company...")
    
    engine = AIReadinessScoringEngine()
    
    # Perfect company data
    hunter_data = {
        "size": "10000+",
        "industry": "artificial intelligence",
        "key_contacts": [
            {"title": "CTO", "seniority": "executive"},
            {"title": "VP Engineering", "seniority": "executive"},
            {"title": "ML Engineer", "seniority": "senior"},
            {"title": "Data Scientist", "seniority": "senior"},
            {"title": "AI Engineer", "seniority": "senior"}
        ]
    }
    
    web_data = {
        "ai_mentions_count": 50,
        "tech_stack_detected": ["tensorflow", "pytorch", "aws", "kubernetes", 
                               "docker", "python", "react", "spark", "jupyter"],
        "careers_signals": {
            "ai_roles": ["ml engineer", "data scientist", "ai engineer"],
            "tech_roles_count": 25
        }
    }
    
    result = engine.calculate_ai_readiness_score(
        hunter_data=hunter_data,
        web_scraping_data=web_data
    )
    
    print(f"✓ Perfect company score: {result['overall_score']}/100")
    print(f"  Component scores: {json.dumps(result['component_scores'], indent=2)}")
    print(f"  Readiness category: {result['readiness_category']}")
    print(f"  Confidence: {result['confidence']}")
    
    assert result['overall_score'] >= 80, "Perfect company should score >= 80"
    assert result['readiness_category'] == "AI-Ready Leader"


def test_poor_company():
    """Test scoring with a company not ready for AI"""
    print("\n3. Testing company not ready for AI...")
    
    engine = AIReadinessScoringEngine()
    
    # Poor AI readiness data
    hunter_data = {
        "size": "11-50",
        "industry": "non-profit",
        "key_contacts": [
            {"title": "Office Manager", "seniority": "senior"}
        ]
    }
    
    web_data = {
        "ai_mentions_count": 0,
        "tech_stack_detected": [],
        "careers_signals": {
            "ai_roles": [],
            "tech_roles_count": 0
        }
    }
    
    result = engine.calculate_ai_readiness_score(
        hunter_data=hunter_data,
        web_scraping_data=web_data
    )
    
    print(f"✓ Poor company score: {result['overall_score']}/100")
    print(f"  Component scores: {json.dumps(result['component_scores'], indent=2)}")
    print(f"  Readiness category: {result['readiness_category']}")
    
    assert result['overall_score'] < 40, "Poor company should score < 40"
    assert result['readiness_category'] in ["Not Yet Ready", "Early Stage"]


def test_missing_data_handling():
    """Test scoring with missing/incomplete data"""
    print("\n4. Testing missing data handling...")
    
    engine = AIReadinessScoringEngine()
    
    # Test with no data
    result1 = engine.calculate_ai_readiness_score()
    print(f"✓ No data score: {result1['overall_score']}/100")
    assert result1['confidence'] <= 0.3, "Low confidence with no data"
    
    # Test with only Hunter data
    result2 = engine.calculate_ai_readiness_score(
        hunter_data={"size": "1000-5000", "industry": "technology"}
    )
    print(f"✓ Only Hunter data score: {result2['overall_score']}/100")
    assert result2['overall_score'] > 0, "Should handle partial data"
    
    # Test with only web scraping data
    result3 = engine.calculate_ai_readiness_score(
        web_scraping_data={"ai_mentions_count": 15, "tech_stack_detected": ["python", "aws"]}
    )
    print(f"✓ Only web data score: {result3['overall_score']}/100")
    assert result3['overall_score'] > 0, "Should handle partial data"


def test_industry_scoring():
    """Test industry-specific scoring"""
    print("\n5. Testing industry-specific scoring...")
    
    engine = AIReadinessScoringEngine()
    
    industries = [
        ("artificial intelligence", 95),
        ("technology", 85),
        ("banking", 65),
        ("healthcare", 60),
        ("retail", 55),
        ("government", 40),
        ("unknown industry", 50)  # Should use default
    ]
    
    for industry, expected_score in industries:
        result = engine._calculate_industry_score(
            {"industry": industry}, None
        )
        print(f"✓ {industry}: {result} (expected ~{expected_score})")
        assert abs(result - expected_score) <= 5, f"Industry score mismatch for {industry}"


def test_tech_hiring_calculation():
    """Test tech hiring score calculation"""
    print("\n6. Testing tech hiring score calculation...")
    
    engine = AIReadinessScoringEngine()
    
    # Test with tech executives
    hunter_data = {
        "key_contacts": [
            {"title": "CTO", "seniority": "executive"},
            {"title": "VP of Engineering", "seniority": "executive"},
            {"title": "Director of Data Science", "seniority": "executive"}
        ]
    }
    
    score = engine._calculate_tech_hiring_score(hunter_data, None, None)
    print(f"✓ Tech executives score: {score}")
    assert score >= 50, "Multiple tech executives should score well"
    
    # Test with AI roles in careers
    web_data = {
        "careers_signals": {
            "ai_roles": ["machine learning engineer", "data scientist"],
            "tech_roles_count": 15
        }
    }
    
    score2 = engine._calculate_tech_hiring_score(None, web_data, None)
    print(f"✓ AI roles hiring score: {score2}")
    assert score2 >= 40, "AI roles should score well"


def test_ai_mentions_calculation():
    """Test AI mentions score calculation"""
    print("\n7. Testing AI mentions score calculation...")
    
    engine = AIReadinessScoringEngine()
    
    test_cases = [
        (0, 15),    # No mentions
        (5, 30),    # Few mentions
        (12, 60),   # Moderate mentions
        (25, 75),   # Many mentions
        (35, 90),   # Very high mentions
    ]
    
    for mentions, expected_min in test_cases:
        score = engine._calculate_ai_mentions_score(
            {"ai_mentions_count": mentions}, None
        )
        print(f"✓ {mentions} mentions: {score} (expected >= {expected_min})")
        assert score >= expected_min, f"Score too low for {mentions} mentions"


def test_company_size_calculation():
    """Test company size score calculation"""
    print("\n8. Testing company size score calculation...")
    
    engine = AIReadinessScoringEngine()
    
    sizes = [
        ("10000+", 85),
        ("5000-10000", 70),
        ("1000-5000", 70),
        ("100-1000", 60),
        ("11-50", 50),
        ("1-10", 40)
    ]
    
    for size, expected in sizes:
        score = engine._calculate_company_size_score(
            {"size": size}, None
        )
        print(f"✓ Size {size}: {score} (expected {expected})")
        assert abs(score - expected) <= 5, f"Size score mismatch for {size}"


def test_tech_modernization_calculation():
    """Test technology modernization score calculation"""
    print("\n9. Testing tech modernization score calculation...")
    
    engine = AIReadinessScoringEngine()
    
    # Test with modern tech stack
    web_data = {
        "tech_stack_detected": [
            "aws", "kubernetes", "docker",  # Cloud (30 points max)
            "react", "python", "typescript",  # Modern (30 points max)
            "tensorflow", "pytorch", "jupyter"  # AI/ML (40 points max)
        ]
    }
    
    score = engine._calculate_tech_modernization_score(web_data, None)
    print(f"✓ Modern tech stack score: {score}")
    assert score >= 70, "Modern tech stack should score well"
    
    # Test with legacy stack (should score 0 as it matches no modern patterns)
    web_data2 = {
        "tech_stack_detected": ["php", "mysql"]
    }
    
    score2 = engine._calculate_tech_modernization_score(web_data2, None)
    print(f"✓ Legacy tech stack score: {score2}")
    assert score2 == 0, "Pure legacy tech with no modern elements should score 0"
    
    # Test with empty stack (should get default 40)
    web_data3 = {
        "tech_stack_detected": []
    }
    
    score3 = engine._calculate_tech_modernization_score(web_data3, None)
    print(f"✓ Empty tech stack score: {score3}")
    assert score3 == 40, "Empty tech stack should get default score of 40"


def test_recommendations_generation():
    """Test recommendations generation logic"""
    print("\n10. Testing recommendations generation...")
    
    engine = AIReadinessScoringEngine()
    
    # Low scores
    component_scores = {
        "tech_hiring": 30,
        "ai_mentions": 25,
        "company_size": 50,
        "industry_adoption": 60,
        "tech_modernization": 35
    }
    
    recommendations = engine._generate_recommendations(component_scores, 40)
    print(f"✓ Generated {len(recommendations)} recommendations for low scores")
    recommendations_str = " ".join(recommendations)
    assert "AI/ML talent" in recommendations_str
    assert "AI strategy" in recommendations_str
    assert "technology stack" in recommendations_str
    
    # High scores
    component_scores2 = {
        "tech_hiring": 85,
        "ai_mentions": 80,
        "company_size": 75,
        "industry_adoption": 85,
        "tech_modernization": 80
    }
    
    recommendations2 = engine._generate_recommendations(component_scores2, 81)
    print(f"✓ Generated {len(recommendations2)} recommendations for high scores")
    assert "ModelML" in str(recommendations2)


def test_readiness_categories():
    """Test readiness category assignment"""
    print("\n11. Testing readiness category assignment...")
    
    engine = AIReadinessScoringEngine()
    
    test_scores = [
        (85, "AI-Ready Leader"),
        (75, "Strong Potential"),
        (55, "Emerging Interest"),
        (40, "Early Stage"),
        (25, "Not Yet Ready")
    ]
    
    for score, expected_category in test_scores:
        category = engine._get_readiness_category(score)
        print(f"✓ Score {score}: {category}")
        assert category == expected_category, f"Wrong category for score {score}"


def test_confidence_calculation():
    """Test confidence score calculation"""
    print("\n12. Testing confidence calculation...")
    
    engine = AIReadinessScoringEngine()
    
    # Full data should have high confidence
    result_full = engine.calculate_ai_readiness_score(
        hunter_data={"size": "1000+", "industry": "tech", "key_contacts": [{"title": "CTO"}]},
        web_scraping_data={"ai_mentions_count": 20, "tech_stack_detected": ["python"]},
        clearbit_data={"employees": 1000, "tech_stack": ["aws"]}
    )
    print(f"✓ Full data confidence: {result_full['confidence']}")
    assert result_full['confidence'] >= 0.7, "Full data should have high confidence"
    
    # Minimal data should have low confidence
    result_minimal = engine.calculate_ai_readiness_score()
    print(f"✓ No data confidence: {result_minimal['confidence']}")
    assert result_minimal['confidence'] <= 0.3, "No data should have low confidence"


def test_strengths_weaknesses_identification():
    """Test identification of strengths and weaknesses"""
    print("\n13. Testing strengths and weaknesses identification...")
    
    engine = AIReadinessScoringEngine()
    
    component_scores = {
        "tech_hiring": 85,  # Strength
        "ai_mentions": 75,  # Strength
        "company_size": 35,  # Weakness
        "industry_adoption": 80,  # Strength
        "tech_modernization": 30  # Weakness
    }
    
    strengths = engine._identify_strengths(component_scores)
    weaknesses = engine._identify_weaknesses(component_scores)
    
    print(f"✓ Identified {len(strengths)} strengths: {strengths}")
    print(f"✓ Identified {len(weaknesses)} weaknesses: {weaknesses}")
    
    assert len(strengths) >= 3, "Should identify multiple strengths"
    assert len(weaknesses) >= 2, "Should identify multiple weaknesses"
    assert "technical team" in str(strengths).lower()
    assert "legacy technology" in str(weaknesses).lower()


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n14. Testing edge cases...")
    
    engine = AIReadinessScoringEngine()
    
    # Test with extreme values
    web_data_extreme = {
        "ai_mentions_count": 10000,  # Extremely high
        "tech_stack_detected": ["ai"] * 100,  # Many duplicates
        "careers_signals": {
            "ai_roles": ["ml"] * 50,
            "tech_roles_count": 1000
        }
    }
    
    result = engine.calculate_ai_readiness_score(web_scraping_data=web_data_extreme)
    print(f"✓ Extreme values score: {result['overall_score']}")
    assert result['overall_score'] <= 100, "Score should be capped at 100"
    assert result['overall_score'] >= 0, "Score should be at least 0"
    
    # Test with None values
    result_none = engine.calculate_ai_readiness_score(
        hunter_data={"size": None, "industry": None, "key_contacts": None}
    )
    print(f"✓ None values handled: {result_none['overall_score']}")
    assert isinstance(result_none['overall_score'], (int, float)), "Should handle None gracefully"
    
    # Test with empty strings
    result_empty = engine.calculate_ai_readiness_score(
        hunter_data={"size": "", "industry": "", "key_contacts": []}
    )
    print(f"✓ Empty values handled: {result_empty['overall_score']}")
    assert isinstance(result_empty['overall_score'], (int, float)), "Should handle empty strings"


def test_real_company_scenarios():
    """Test with realistic company scenarios"""
    print("\n15. Testing real company scenarios...")
    
    engine = AIReadinessScoringEngine()
    
    # Scenario 1: Large bank exploring AI
    bank_data = {
        "hunter_data": {
            "size": "10000+",
            "industry": "banking",
            "key_contacts": [
                {"title": "Chief Digital Officer", "seniority": "executive"},
                {"title": "VP Technology", "seniority": "executive"}
            ]
        },
        "web_scraping_data": {
            "ai_mentions_count": 8,
            "tech_stack_detected": ["java", "oracle", "aws"],
            "careers_signals": {
                "ai_roles": ["data scientist"],
                "tech_roles_count": 10
            }
        }
    }
    
    result = engine.calculate_ai_readiness_score(**bank_data)
    print(f"✓ Large bank scenario:")
    print(f"  Score: {result['overall_score']}")
    print(f"  Category: {result['readiness_category']}")
    print(f"  Top recommendation: {result['recommendations'][0] if result['recommendations'] else 'None'}")
    assert 50 <= result['overall_score'] <= 75, "Bank should score moderate"
    
    # Scenario 2: AI startup
    startup_data = {
        "hunter_data": {
            "size": "11-50",
            "industry": "artificial intelligence",
            "key_contacts": [
                {"title": "CTO", "seniority": "executive"},
                {"title": "ML Engineer", "seniority": "senior"}
            ]
        },
        "web_scraping_data": {
            "ai_mentions_count": 45,
            "tech_stack_detected": ["tensorflow", "pytorch", "kubernetes", "python"],
            "careers_signals": {
                "ai_roles": ["ml engineer", "ai researcher"],
                "tech_roles_count": 8
            }
        }
    }
    
    result2 = engine.calculate_ai_readiness_score(**startup_data)
    print(f"✓ AI startup scenario:")
    print(f"  Score: {result2['overall_score']}")
    print(f"  Category: {result2['readiness_category']}")
    assert result2['overall_score'] >= 70, "AI startup should score high"


def run_all_tests():
    """Run all scoring engine tests"""
    print("=" * 60)
    print("AI READINESS SCORING ENGINE - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_scoring_weights,
        test_perfect_company,
        test_poor_company,
        test_missing_data_handling,
        test_industry_scoring,
        test_tech_hiring_calculation,
        test_ai_mentions_calculation,
        test_company_size_calculation,
        test_tech_modernization_calculation,
        test_recommendations_generation,
        test_readiness_categories,
        test_confidence_calculation,
        test_strengths_weaknesses_identification,
        test_edge_cases,
        test_real_company_scenarios
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n✅ ALL TESTS PASSED! Scoring engine is fully functional.")
    else:
        print("\n❌ Some tests failed. Review and fix issues.")
    
    exit(0 if success else 1)