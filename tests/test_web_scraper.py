"""
Test Web Scraping Service functionality
"""

import sys
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.web_scraper import WebScraperService


async def test_web_scraper():
    """Test web scraping service"""
    
    print("Testing Web Scraping Service...")
    
    scraper = WebScraperService()
    
    # Test 1: Scrape a known website (example.com is safe for testing)
    print("\n1. Testing with example.com...")
    result = await scraper.scrape_company_website("example.com")
    assert result is not None
    assert result["domain"] == "example.com"
    print(f"✓ Scraped example.com")
    print(f"  AI mentions: {result['ai_mentions_count']}")
    print(f"  Tech stack detected: {result['tech_stack_detected']}")
    
    # Test 2: Test with a tech company website (httpbin.org for testing)
    print("\n2. Testing with httpbin.org (test site)...")
    result2 = await scraper.scrape_company_website("httpbin.org")
    assert result2 is not None
    print(f"✓ Scraped httpbin.org")
    
    # Test 3: Test with invalid domain
    print("\n3. Testing with invalid domain...")
    result3 = await scraper.scrape_company_website("this-domain-does-not-exist-12345.com")
    assert result3 is not None  # Should return empty result, not crash
    assert result3["ai_readiness_signals"]["score"] == 0
    print("✓ Handled invalid domain gracefully")
    
    # Test 4: Test AI keyword detection
    print("\n4. Testing AI keyword detection...")
    # Create a mock scraper method test
    text = "we use artificial intelligence and machine learning for deep learning applications with tensorflow"
    count = scraper._count_ai_mentions(text)
    assert count > 0
    print(f"✓ AI keyword detection working: found {count} mentions")
    
    # Test 5: Test tech stack detection
    print("\n5. Testing tech stack detection...")
    text2 = "our stack includes aws, kubernetes, docker, react, and python"
    tech = scraper._detect_tech_stack(text2)
    assert len(tech) > 0
    assert "aws" in tech
    assert "kubernetes" in tech
    print(f"✓ Tech stack detection: {tech}")
    
    print("\n✅ All web scraper tests passed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_web_scraper())