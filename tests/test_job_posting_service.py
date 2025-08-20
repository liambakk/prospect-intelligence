"""
Comprehensive test suite for Job Posting Service
Tests JSearch API integration, job filtering, and AI/ML keyword extraction
"""

import sys
from pathlib import Path
import asyncio
import json

sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.job_posting_service import JobPostingService


async def test_job_posting_service():
    """Test job posting service with various scenarios"""
    
    print("=" * 60)
    print("JOB POSTING SERVICE - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    service = JobPostingService()
    
    # Test 1: Mock data for Google (AI-heavy company)
    print("\n1. Testing with Google (mock data - AI-heavy company)...")
    result = await service.search_company_jobs("google")
    assert result is not None
    assert result["company_name"] == "google"
    assert result["ai_ml_jobs_count"] > 10
    assert result["ai_hiring_intensity"] == "very_high"
    assert len(result["top_ai_technologies"]) > 0
    print(f"✓ Google analysis:")
    print(f"  - Total jobs: {result['total_jobs_found']}")
    print(f"  - AI/ML jobs: {result['ai_ml_jobs_count']}")
    print(f"  - Tech jobs: {result['tech_jobs_count']}")
    print(f"  - AI hiring intensity: {result['ai_hiring_intensity']}")
    print(f"  - Top AI tech: {result['top_ai_technologies'][:3]}")
    
    # Test 2: Mock data for JPMorgan (traditional company exploring AI)
    print("\n2. Testing with JPMorgan (mock data - traditional exploring AI)...")
    result2 = await service.search_company_jobs("jpmorgan")
    assert result2 is not None
    assert result2["ai_ml_jobs_count"] < 10
    assert result2["ai_hiring_intensity"] in ["moderate", "low"]
    print(f"✓ JPMorgan analysis:")
    print(f"  - Total jobs: {result2['total_jobs_found']}")
    print(f"  - AI/ML jobs: {result2['ai_ml_jobs_count']}")
    print(f"  - Tech jobs: {result2['tech_jobs_count']}")
    print(f"  - AI hiring intensity: {result2['ai_hiring_intensity']}")
    
    # Test 3: Unknown company (default mock data)
    print("\n3. Testing with unknown company (default mock data)...")
    result3 = await service.search_company_jobs("SmallStartup123")
    assert result3 is not None
    assert result3["company_name"] == "SmallStartup123"
    assert result3["ai_hiring_intensity"] in ["low", "none"]
    print(f"✓ Unknown company analysis:")
    print(f"  - Total jobs: {result3['total_jobs_found']}")
    print(f"  - AI/ML jobs: {result3['ai_ml_jobs_count']}")
    print(f"  - AI hiring intensity: {result3['ai_hiring_intensity']}")
    
    # Test 4: Test hiring intensity calculation
    print("\n4. Testing hiring intensity calculation...")
    test_cases = [
        (0, 10, "none"),
        (1, 10, "low"),
        (3, 20, "moderate"),
        (6, 30, "high"),
        (12, 40, "very_high")
    ]
    
    for ai_jobs, total_jobs, expected_intensity in test_cases:
        intensity = service._calculate_hiring_intensity(ai_jobs, total_jobs)
        assert intensity == expected_intensity, f"Expected {expected_intensity} for {ai_jobs}/{total_jobs}, got {intensity}"
        print(f"✓ {ai_jobs}/{total_jobs} jobs -> {intensity}")
    
    # Test 5: Test job analysis logic
    print("\n5. Testing job analysis and categorization...")
    mock_jobs = [
        {"job_title": "Senior Machine Learning Engineer", "employer_name": "Test Corp", 
         "job_description": "Work on deep learning models using TensorFlow and PyTorch"},
        {"job_title": "Data Scientist", "employer_name": "Test Corp",
         "job_description": "Analyze data and build predictive models"},
        {"job_title": "Software Engineer", "employer_name": "Test Corp",
         "job_description": "Build scalable web applications"},
        {"job_title": "AI Research Scientist", "employer_name": "Test Corp",
         "job_description": "Research computer vision and NLP algorithms"},
        {"job_title": "DevOps Engineer", "employer_name": "Test Corp",
         "job_description": "Manage cloud infrastructure and CI/CD pipelines"}
    ]
    
    analysis = service._analyze_job_postings("Test Corp", mock_jobs)
    assert analysis["company_name"] == "Test Corp"
    assert analysis["total_jobs_found"] == 5
    assert analysis["ai_ml_jobs_count"] == 3  # ML Engineer, Data Scientist, AI Research
    assert analysis["tech_jobs_count"] == 2  # Software Engineer, DevOps
    assert "tensorflow" in [t["keyword"] for t in analysis["top_ai_technologies"]]
    print(f"✓ Job categorization:")
    print(f"  - AI/ML jobs identified: {analysis['ai_ml_jobs_count']}/5")
    print(f"  - Tech jobs identified: {analysis['tech_jobs_count']}/5")
    print(f"  - Keywords extracted: {len(analysis['tech_stack_signals'])}")
    
    # Test 6: Test caching mechanism
    print("\n6. Testing caching mechanism...")
    # First call (will cache)
    cache_key = service._get_cache_key("TestCompany", "month")
    service._add_to_cache(cache_key, {"test": "data"})
    
    # Second call (should retrieve from cache)
    cached_data = service._get_from_cache(cache_key)
    assert cached_data is not None
    assert cached_data["test"] == "data"
    print("✓ Cache storage and retrieval working")
    
    # Test 7: Test AI/ML keyword detection
    print("\n7. Testing AI/ML keyword extraction...")
    test_description = """
    We are looking for a Machine Learning Engineer to work on our deep learning 
    platform. You will use TensorFlow, PyTorch, and scikit-learn to build 
    neural networks for computer vision and NLP applications. Experience with 
    transformers, BERT, and large language models is a plus.
    """
    
    keywords_found = []
    for keyword in service.AI_ML_KEYWORDS:
        if keyword in test_description.lower():
            keywords_found.append(keyword)
    
    assert "tensorflow" in keywords_found
    assert "pytorch" in keywords_found
    assert "deep learning" in keywords_found
    assert "computer vision" in keywords_found
    assert len(keywords_found) >= 8
    print(f"✓ Found {len(keywords_found)} AI/ML keywords in test description")
    print(f"  Keywords: {keywords_found[:10]}")
    
    # Test 8: Test data structure validation
    print("\n8. Testing response data structure...")
    result = await service.search_company_jobs("google")
    required_fields = [
        "company_name", "total_jobs_found", "ai_ml_jobs_count", 
        "tech_jobs_count", "ai_ml_percentage", "tech_percentage",
        "top_ai_technologies", "recent_job_titles", "ai_hiring_intensity",
        "tech_stack_signals", "analysis_timestamp", "data_source"
    ]
    
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    assert isinstance(result["total_jobs_found"], int)
    assert isinstance(result["ai_ml_jobs_count"], int)
    assert isinstance(result["top_ai_technologies"], list)
    assert isinstance(result["recent_job_titles"], list)
    assert result["data_source"] in ["jsearch_api", "mock_data"]
    print("✓ All required fields present and correctly typed")
    
    print("\n" + "=" * 60)
    print("✅ ALL JOB POSTING SERVICE TESTS PASSED!")
    print("=" * 60)
    
    return True


async def test_with_real_api():
    """Test with real JSearch API if key is configured"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if not os.getenv("RAPIDAPI_KEY"):
        print("\n⚠️  No RapidAPI key found. Skipping real API test.")
        print("   Add RAPIDAPI_KEY to .env to test with real JSearch API")
        return
    
    print("\n" + "=" * 60)
    print("TESTING WITH REAL JSEARCH API")
    print("=" * 60)
    
    service = JobPostingService()
    
    # Test with a real company
    print("\n Testing with Microsoft (real API call)...")
    result = await service.search_company_jobs("Microsoft", date_posted="week", num_pages=1)
    
    if result and result.get("data_source") == "jsearch_api":
        print(f"✓ Real API call successful!")
        print(f"  - Total jobs found: {result['total_jobs_found']}")
        print(f"  - AI/ML jobs: {result['ai_ml_jobs_count']}")
        print(f"  - Tech jobs: {result['tech_jobs_count']}")
        print(f"  - Data source: {result['data_source']}")
        
        if result["recent_job_titles"]:
            print(f"\n  Recent job titles:")
            for job in result["recent_job_titles"][:3]:
                print(f"    - {job['title']} ({job['location']})")
    else:
        print("⚠️  Real API call failed or returned mock data")
        print("   Check your RapidAPI key and rate limits")


if __name__ == "__main__":
    # Run main tests
    asyncio.run(test_job_posting_service())
    
    # Optionally test with real API
    asyncio.run(test_with_real_api())