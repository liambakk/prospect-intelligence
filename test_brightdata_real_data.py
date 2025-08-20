"""
Test BrightData LinkedIn Integration for Real Data
Verifies that actual LinkedIn profiles are fetched, not mock data
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.brightdata_correct_service import BrightDataCorrectService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestBrightDataRealData:
    """Test suite for verifying real LinkedIn data from BrightData"""
    
    def __init__(self):
        self.service = BrightDataCorrectService()
        self.test_results = []
    
    async def test_direct_api_call(self):
        """Test direct BrightData API call with known LinkedIn profiles"""
        print("\n" + "="*60)
        print("TEST 1: Direct BrightData API Call")
        print("="*60)
        
        # Test with real LinkedIn URLs
        test_urls = [
            "https://www.linkedin.com/in/jamie-dimon-97413111/",  # JPMorgan CEO
            "https://www.linkedin.com/in/lori-beer-9257184/"      # JPMorgan CIO
        ]
        
        print(f"Testing with profiles: {test_urls}")
        
        # Trigger scraping
        snapshot_id = await self.service.trigger_scraper(test_urls)
        
        if snapshot_id:
            print(f"✅ Successfully triggered scraper, snapshot_id: {snapshot_id}")
            
            # Get results (with polling)
            print("⏳ Waiting for results (this may take 2-5 minutes)...")
            results = await self.service.get_results(snapshot_id)
            
            if results and len(results) > 0:
                print(f"✅ Got {len(results)} results from BrightData")
                
                # Check if it's real data (not mock)
                is_real = self._verify_real_data(results)
                
                if is_real:
                    print("✅ VERIFIED: This is REAL LinkedIn data!")
                    self._display_profile_data(results[0])
                    return True
                else:
                    print("❌ WARNING: Data appears to be mock/fallback")
                    return False
            else:
                print("❌ No results returned from BrightData")
                return False
        else:
            print("❌ Failed to trigger BrightData scraper")
            return False
    
    async def test_service_method(self):
        """Test the search_linkedin_profiles method with known company"""
        print("\n" + "="*60)
        print("TEST 2: BrightData Service Method")
        print("="*60)
        
        company = "JPMorgan Chase"
        print(f"Testing with company: {company}")
        
        # Call the service method
        results = await self.service.search_linkedin_profiles(company)
        
        if results:
            print(f"✅ Got {len(results)} profiles")
            
            # Check first profile
            first_profile = results[0]
            
            # Check for mock data indicators
            if first_profile.get("name") == "[Research Needed]":
                print("❌ Returned mock data (name = '[Research Needed]')")
                return False
            
            # Check for real data indicators
            real_indicators = 0
            if first_profile.get("linkedin_url") and "linkedin.com/in/" in first_profile.get("linkedin_url", ""):
                real_indicators += 1
                print(f"✅ Has real LinkedIn URL: {first_profile.get('linkedin_url')}")
            
            if first_profile.get("name") and first_profile.get("name") != "[Research Needed]":
                real_indicators += 1
                print(f"✅ Has real name: {first_profile.get('name')}")
            
            if first_profile.get("title") and "Unknown" not in first_profile.get("title", ""):
                real_indicators += 1
                print(f"✅ Has real title: {first_profile.get('title')}")
            
            if first_profile.get("experience_years", 0) > 0:
                real_indicators += 1
                print(f"✅ Has experience years: {first_profile.get('experience_years')}")
            
            if real_indicators >= 3:
                print(f"\n✅ VERIFIED: Real LinkedIn data (passed {real_indicators}/4 checks)")
                self._display_profile_data(first_profile)
                return True
            else:
                print(f"\n❌ Appears to be mock data (only {real_indicators}/4 real indicators)")
                return False
        else:
            print("❌ No profiles returned")
            return False
    
    async def test_full_api_integration(self):
        """Test the full API endpoint with comprehensive analysis"""
        print("\n" + "="*60)
        print("TEST 3: Full API Integration Test")
        print("="*60)
        
        url = "http://localhost:8000/analyze/comprehensive"
        payload = {
            "name": "JPMorgan Chase",
            "domain": "jpmorganchase.com"
        }
        
        print(f"Testing API endpoint: {url}")
        print(f"Company: {payload['name']}")
        
        async with httpx.AsyncClient(timeout=300) as client:
            try:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ API returned successfully")
                    
                    # Check decision makers
                    decision_makers = data.get("recommendations", {}).get("decision_makers", [])
                    
                    if decision_makers:
                        print(f"✅ Found {len(decision_makers)} decision makers")
                        
                        # Check first decision maker
                        first_dm = decision_makers[0]
                        
                        # Look for BrightData LinkedIn data
                        if first_dm.get("role") == "LinkedIn Verified Profile":
                            print("✅ Has LinkedIn Verified Profile (from BrightData)")
                            print(f"   Name: {first_dm.get('name')}")
                            print(f"   Title: {first_dm.get('title')}")
                            print(f"   LinkedIn: {first_dm.get('linkedin')}")
                            
                            # Check talking points for real data
                            talking_points = first_dm.get("talking_points", [])
                            if any("expertise" in tp for tp in talking_points):
                                print("✅ Has personalized talking points from LinkedIn data")
                            
                            return True
                        else:
                            print(f"⚠️ First decision maker role: {first_dm.get('role')}")
                            print("   May be using fallback data")
                    
                    # Check data sources
                    data_sources = data.get("data_sources", {})
                    print(f"\nData Sources Status:")
                    print(f"  Hunter.io: {'✅' if data_sources.get('hunter_io') else '❌'}")
                    print(f"  Job Postings: {'✅' if data_sources.get('job_postings') else '❌'}")
                    print(f"  News: {'✅' if data_sources.get('news_articles') else '❌'}")
                    print(f"  BrightData: {'✅' if data_sources.get('brightdata') else '❌'}")
                    
                    return data_sources.get("brightdata", False)
                else:
                    print(f"❌ API returned error: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ API call failed: {e}")
                return False
    
    def _verify_real_data(self, results: list) -> bool:
        """Verify if the data is real LinkedIn data or mock"""
        if not results:
            return False
        
        # Check for patterns that indicate real data
        real_indicators = []
        
        for result in results[:1]:  # Check first result
            # Real LinkedIn data should have these fields
            if result.get("url") and "linkedin.com/in/" in result.get("url", ""):
                real_indicators.append("Has real LinkedIn URL")
            
            if result.get("name") and result.get("name") != "[Research Needed]":
                real_indicators.append("Has real name")
            
            if result.get("position") or result.get("title"):
                real_indicators.append("Has position/title")
            
            if result.get("current_company_name"):
                real_indicators.append("Has company name")
            
            # Check for fields that indicate scraped data
            if result.get("about") and len(result.get("about", "")) > 50:
                real_indicators.append("Has detailed about section")
            
            if result.get("experience") and isinstance(result.get("experience"), list):
                real_indicators.append("Has experience history")
        
        print(f"\nReal Data Indicators Found: {len(real_indicators)}/6")
        for indicator in real_indicators:
            print(f"  ✅ {indicator}")
        
        # If we have at least 3 real indicators, it's likely real data
        return len(real_indicators) >= 3
    
    def _display_profile_data(self, profile: Dict[str, Any]):
        """Display profile data for verification"""
        print("\n📋 Profile Data Sample:")
        print("-" * 40)
        
        # Display key fields
        fields_to_show = [
            "name", "title", "position", "company", 
            "current_company_name", "location", "url", 
            "linkedin_url", "about", "followers", "connections"
        ]
        
        for field in fields_to_show:
            if field in profile:
                value = profile[field]
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {field}: {value}")
        
        # Check for experience
        if "experience" in profile:
            exp = profile["experience"]
            if isinstance(exp, list):
                print(f"  experience: {len(exp)} positions")
            elif isinstance(exp, int):
                print(f"  experience_years: {exp}")
        
        print("-" * 40)
    
    async def run_all_tests(self):
        """Run all BrightData tests"""
        print("\n" + "="*60)
        print("BRIGHTDATA REAL DATA VERIFICATION TEST SUITE")
        print("="*60)
        print("\nThis will test if BrightData returns REAL LinkedIn data")
        print("Note: Tests may take 2-5 minutes due to scraping time")
        
        tests = [
            ("Direct API Call", self.test_direct_api_call),
            ("Service Method", self.test_service_method),
            ("Full API Integration", self.test_full_api_integration)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ Test '{test_name}' failed with error: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:25} {status}")
        
        print("-" * 60)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 SUCCESS: BrightData is returning REAL LinkedIn data!")
        elif passed > 0:
            print(f"\n⚠️ PARTIAL: Some tests passed ({passed}/{total}), but not all")
            print("BrightData may be working but slow or limited")
        else:
            print("\n❌ FAILURE: BrightData is NOT returning real data")
            print("System is falling back to mock data")
        
        return passed == total


async def main():
    """Main test runner"""
    tester = TestBrightDataRealData()
    success = await tester.run_all_tests()
    
    # Return exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    print("Starting BrightData Real Data Tests...")
    print("Note: Ensure the API server is running (python src/main.py)")
    asyncio.run(main())