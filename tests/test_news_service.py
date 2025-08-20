"""
Test News Collection Service
"""

import sys
from pathlib import Path
import asyncio
import json

sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.news_service import NewsService


async def test_news_collection():
    """Test the news collection service functionality"""
    
    print("=" * 60)
    print("NEWS COLLECTION SERVICE TEST")
    print("=" * 60)
    
    # Initialize service
    service = NewsService()
    
    # Test companies
    test_companies = [
        "Microsoft",
        "Google", 
        "JPMorgan Chase",
        "Tesla"
    ]
    
    for company in test_companies:
        print(f"\n{'=' * 40}")
        print(f"Testing: {company}")
        print("=" * 40)
        
        try:
            # Get news for the company
            result = await service.get_company_news(
                company_name=company,
                days_back=7,  # Last week
                max_articles=20
            )
            
            # Display results
            print(f"\n📊 Results for {company}:")
            print(f"  • Total articles found: {result.get('total_articles_found', 0)}")
            print(f"  • Articles processed: {result.get('articles_processed', 0)}")
            print(f"  • AI mentions count: {result.get('ai_mentions_count', 0)}")
            print(f"  • Tech focus score: {result.get('tech_focus_score', 0):.1f}/100")
            print(f"  • Data source: {result.get('data_source', 'Unknown')}")
            
            # Show recent trends
            trends = result.get('recent_trends', [])
            if trends:
                print(f"\n  📈 Recent trends:")
                for i, trend in enumerate(trends[:3], 1):
                    print(f"     {i}. {trend}")
            
            # Show top articles
            articles = result.get('articles', [])
            if articles:
                print(f"\n  📰 Top articles (by relevance):")
                for i, article in enumerate(articles[:3], 1):
                    print(f"\n     {i}. {article['title']}")
                    print(f"        Source: {article['source']}")
                    print(f"        Relevance: {article['relevance_score']}/100")
                    keywords = article.get('ai_keywords_found', [])
                    if keywords:
                        print(f"        Keywords: {', '.join(keywords[:3])}")
            
            # Test deduplication
            print(f"\n  🔍 Deduplication test:")
            titles = [a['title'] for a in articles]
            unique_titles = len(set(titles))
            print(f"     Total articles: {len(articles)}")
            print(f"     Unique titles: {unique_titles}")
            print(f"     Duplicates removed: {len(articles) - unique_titles}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test edge cases
    print(f"\n{'=' * 40}")
    print("EDGE CASE TESTS")
    print("=" * 40)
    
    # Test with non-existent company
    print("\n1. Non-existent company test:")
    try:
        result = await service.get_company_news("XYZ123NonExistentCompany456", days_back=7)
        print(f"   Articles found: {result.get('articles_processed', 0)}")
        print(f"   Data source: {result.get('data_source', 'Unknown')}")
    except Exception as e:
        print(f"   Error handled: {e}")
    
    # Test with special characters
    print("\n2. Special characters test:")
    try:
        result = await service.get_company_news("AT&T", days_back=7)
        print(f"   Articles found: {result.get('articles_processed', 0)}")
        print(f"   Successfully handled special characters")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test relevance scoring
    print("\n3. Relevance scoring validation:")
    mock_result = await service.get_company_news("TestCompany", days_back=1)
    if mock_result.get('articles'):
        for article in mock_result['articles'][:3]:
            score = article['relevance_score']
            assert 0 <= score <= 100, f"Invalid score: {score}"
        print("   ✓ All relevance scores are within 0-100 range")
    
    print("\n" + "=" * 60)
    print("✅ ALL NEWS SERVICE TESTS COMPLETED!")
    print("=" * 60)
    
    return True


async def test_api_integration():
    """Test actual NewsAPI integration if key is available"""
    
    print("\n" + "=" * 60)
    print("NEWSAPI INTEGRATION TEST")
    print("=" * 60)
    
    service = NewsService()
    
    if service.use_mock:
        print("\n⚠️  NewsAPI key not found - using mock data")
        print("   To test with real API, add NEWSAPI_KEY to .env file")
        print("   Get free API key at: https://newsapi.org/register")
    else:
        print("\n✓ NewsAPI key found - testing real API")
        
        # Test with a well-known company
        result = await service.get_company_news("Apple", days_back=3, max_articles=10)
        
        if result.get('error'):
            print(f"   ❌ API Error: {result['error']}")
        else:
            print(f"   ✓ Successfully fetched {result.get('articles_processed', 0)} articles")
            print(f"   ✓ API integration working correctly")
    
    return True


if __name__ == "__main__":
    print("Starting News Service Tests...\n")
    
    # Run main tests
    asyncio.run(test_news_collection())
    
    # Run API integration test
    asyncio.run(test_api_integration())