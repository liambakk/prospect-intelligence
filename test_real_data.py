#!/usr/bin/env python3
"""
Test script to verify that the system is using real data instead of mock data
Tests all API integrations and data sources
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any
import sys

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_COMPANIES = [
    {"name": "JPMorgan Chase", "domain": "jpmorganchase.com"},
    {"name": "Google", "domain": "google.com"},
    {"name": "BlackRock", "domain": "blackrock.com"}
]

# Mock data patterns to detect
MOCK_INDICATORS = {
    "scores": [24, 50, 75],  # Common mock scores
    "employee_counts": [2500, 1000, 5000],  # Mock employee counts
    "phrases": [
        "Mock data",
        "Test data",
        "Example company",
        "No data available",
        "Limited data available",
        "[Research needed]",
        "[Identify",
        "Unknown sector"
    ],
    "mock_emails": ["test@example.com", "mock@company.com"],
    "mock_job_counts": [0, 10, 25],  # Suspiciously round numbers
}

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {test_name}")
    if details:
        print(f"         {details}")

async def test_api_endpoints():
    """Test that all API endpoints are accessible"""
    print_header("Testing API Endpoints")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health endpoint
        try:
            response = await client.get(f"{BASE_URL}/health")
            passed = response.status_code == 200
            print_test("Health endpoint", passed, f"Status: {response.status_code}")
        except Exception as e:
            print_test("Health endpoint", False, str(e))
        
        # Test main page
        try:
            response = await client.get(BASE_URL)
            passed = response.status_code == 200
            print_test("Main page", passed, f"Status: {response.status_code}")
        except Exception as e:
            print_test("Main page", False, str(e))

async def analyze_company(company: Dict[str, str]) -> Dict[str, Any]:
    """Analyze a single company and return results"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/analyze/comprehensive",
            json={"name": company["name"], "domain": company["domain"]}
        )
        
        if response.status_code != 200:
            raise Exception(f"Analysis failed: {response.status_code} - {response.text}")
        
        return response.json()

def check_for_mock_data(data: Dict[str, Any], company_name: str) -> Dict[str, bool]:
    """Check if the data contains mock indicators"""
    tests = {}
    
    # 1. Check AI readiness score
    score = data.get("ai_readiness_score", 0)
    tests["score_not_mock"] = score not in MOCK_INDICATORS["scores"]
    tests["score_details"] = f"Score: {score}"
    
    # 2. Check for mock phrases in company data
    company_data_str = json.dumps(data.get("company_data", {})).lower()
    has_mock_phrases = any(phrase.lower() in company_data_str for phrase in MOCK_INDICATORS["phrases"])
    tests["no_mock_phrases"] = not has_mock_phrases
    
    # 3. Check data sources
    sources = data.get("data_sources", {})
    active_sources = sum(1 for v in sources.values() if v)
    tests["multiple_data_sources"] = active_sources >= 3
    tests["sources_details"] = f"Active sources: {active_sources}/7"
    
    # 4. Check job postings
    job_data = data.get("company_data", {}).get("job_postings", {})
    total_jobs = job_data.get("total_jobs", 0)
    ai_jobs = job_data.get("ai_ml_jobs", 0)
    tests["real_job_data"] = total_jobs > 0 and total_jobs not in MOCK_INDICATORS["mock_job_counts"]
    tests["job_details"] = f"Total jobs: {total_jobs}, AI/ML jobs: {ai_jobs}"
    
    # 5. Check decision makers
    decision_makers = data.get("recommendations", {}).get("decision_makers", [])
    has_real_names = any(
        dm.get("name") and 
        not any(mock in dm.get("name", "") for mock in ["[Identify", "[Research", "Unknown"])
        for dm in decision_makers
    )
    tests["real_decision_makers"] = has_real_names
    tests["dm_count"] = f"Decision makers found: {len(decision_makers)}"
    
    # 6. Check LinkedIn data
    linkedin_profile = data.get("company_data", {}).get("linkedin_profile", {})
    has_linkedin = (
        linkedin_profile.get("employee_count") and 
        linkedin_profile.get("employee_count") > 0
    )
    tests["linkedin_data_present"] = has_linkedin or sources.get("linkedin", False)
    
    # 7. Check news data
    news_data = data.get("company_data", {}).get("news_insights", {})
    articles_found = news_data.get("total_articles", 0)
    tests["news_data_present"] = articles_found > 0
    tests["news_details"] = f"News articles: {articles_found}"
    
    # 8. Check tech signals
    tech_signals = data.get("company_data", {}).get("tech_signals", {})
    ai_mentions = tech_signals.get("ai_mentions", 0)
    tech_stack = tech_signals.get("tech_stack", [])
    tests["tech_signals_present"] = ai_mentions > 0 or len(tech_stack) > 0
    tests["tech_details"] = f"AI mentions: {ai_mentions}, Tech stack items: {len(tech_stack)}"
    
    # 9. Check component scores variety
    component_scores = data.get("component_scores", {})
    unique_scores = len(set(component_scores.values()))
    tests["varied_component_scores"] = unique_scores > 3
    tests["component_variety"] = f"Unique component scores: {unique_scores}"
    
    # 10. Check for BrightData integration
    brightdata_active = sources.get("brightdata", False)
    tests["brightdata_integration"] = brightdata_active
    
    return tests

async def run_comprehensive_tests():
    """Run all tests"""
    print("\n" + "🔍 PROSPECT INTELLIGENCE REAL DATA VERIFICATION TEST 🔍")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test API endpoints first
    await test_api_endpoints()
    
    # Test each company
    all_passed = True
    for company in TEST_COMPANIES:
        print_header(f"Testing {company['name']}")
        
        try:
            # Analyze the company
            print(f"  Analyzing {company['name']}...")
            data = await analyze_company(company)
            
            # Check for mock data
            tests = check_for_mock_data(data, company['name'])
            
            # Print results
            company_passed = True
            for test_name, result in tests.items():
                if test_name.endswith("_details"):
                    continue  # Skip detail entries
                    
                details = tests.get(f"{test_name[:-len('_details')]}_details", "")
                if isinstance(result, bool):
                    print_test(test_name.replace("_", " ").title(), result, tests.get(test_name + "_details", ""))
                    if not result:
                        company_passed = False
                else:
                    print(f"         {test_name}: {result}")
            
            if not company_passed:
                all_passed = False
                
            # Print summary for this company
            print(f"\n  Summary for {company['name']}:")
            print(f"  - AI Readiness Score: {data.get('ai_readiness_score')}")
            print(f"  - Readiness Category: {data.get('readiness_category')}")
            print(f"  - Confidence: {data.get('confidence')}%")
            
            # Print active data sources
            sources = data.get("data_sources", {})
            active = [k for k, v in sources.items() if v]
            print(f"  - Active Data Sources: {', '.join(active)}")
            
        except Exception as e:
            print_test(f"Analysis of {company['name']}", False, str(e))
            all_passed = False
    
    # Final summary
    print_header("TEST SUMMARY")
    if all_passed:
        print("  🎉 ALL TESTS PASSED! The system is using REAL DATA!")
        print("  ✅ No mock data patterns detected")
        print("  ✅ Multiple data sources are active")
        print("  ✅ Real-time data is being fetched and processed")
    else:
        print("  ⚠️ SOME TESTS FAILED - Review the results above")
        print("  - Some data sources may not be fully configured")
        print("  - Check API keys and service availability")
    
    print("\n" + "="*60)
    return all_passed

async def test_individual_apis():
    """Test individual API services directly"""
    print_header("Testing Individual API Services")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test Hunter.io
    hunter_key = os.getenv("HUNTER_API_KEY")
    if hunter_key:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.hunter.io/v2/domain-search?domain=google.com&api_key={hunter_key}"
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}
            print_test("Hunter.io API", passed, f"Organization: {data.get('data', {}).get('organization', 'N/A')}")
    
    # Test NewsAPI
    news_key = os.getenv("NEWS_API_KEY")
    if news_key:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://newsapi.org/v2/everything?q=JPMorgan&apiKey={news_key}&pageSize=1"
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}
            print_test("NewsAPI", passed, f"Articles found: {data.get('totalResults', 0)}")
    
    # Test RapidAPI JSearch
    rapid_key = os.getenv("RAPIDAPI_KEY")
    if rapid_key:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://jsearch.p.rapidapi.com/search?query=Google%20software%20engineer&num_pages=1",
                headers={
                    "X-RapidAPI-Key": rapid_key,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
                }
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}
            print_test("JSearch API", passed, f"Status: {data.get('status', 'N/A')}")
    
    # Test BrightData
    bright_key = os.getenv("BRIGHT_DATA_API")
    if bright_key and bright_key != "your_brightdata_api_key_here":
        print_test("BrightData API", True, "API key configured (actual test requires specific endpoint)")
    else:
        print_test("BrightData API", False, "API key not configured or using placeholder")

if __name__ == "__main__":
    print("\nStarting Real Data Verification Tests...")
    print("Make sure the server is running on http://localhost:8000")
    print("-" * 60)
    
    # Run individual API tests first
    asyncio.run(test_individual_apis())
    
    # Run comprehensive tests
    try:
        result = asyncio.run(run_comprehensive_tests())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)