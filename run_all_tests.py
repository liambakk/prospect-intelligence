#!/usr/bin/env python
"""
Run all tests and generate a comprehensive test report
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_test(test_name, test_file):
    """Run a single test file and return results"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check if test passed
        if result.returncode == 0:
            print(f"✅ {test_name}: PASSED")
            return True, None
        else:
            print(f"❌ {test_name}: FAILED")
            # Extract error message
            error_msg = result.stderr.split('\n')[-2] if result.stderr else "Unknown error"
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {test_name}: TIMEOUT")
        return False, "Test exceeded 30 second timeout"
    except Exception as e:
        print(f"❌ {test_name}: ERROR - {e}")
        return False, str(e)

def main():
    """Run all tests and generate report"""
    
    print("\n" + "="*60)
    print("PROSPECT INTELLIGENCE TOOL - COMPREHENSIVE TEST SUITE")
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Define all tests
    tests_dir = Path("tests")
    tests = [
        ("Database Models", tests_dir / "test_models.py"),
        ("Hunter.io Service", tests_dir / "test_hunter.py"),
        ("Web Scraper", tests_dir / "test_web_scraper.py"),
        ("Scoring Engine", tests_dir / "test_scoring_engine.py"),
        ("Job Posting Service", tests_dir / "test_job_posting_service.py"),
        ("News Service", tests_dir / "test_news_service.py"),
        ("PDF Generation", tests_dir / "test_pdf_generation.py"),
        ("API Integration", tests_dir / "test_integration.py"),
    ]
    
    # Run all tests
    results = {}
    errors = {}
    
    for test_name, test_file in tests:
        if test_file.exists():
            passed, error = run_test(test_name, test_file)
            results[test_name] = passed
            if error:
                errors[test_name] = error
        else:
            print(f"⚠️ {test_name}: Test file not found")
            results[test_name] = False
            errors[test_name] = "Test file not found"
    
    # Generate summary report
    print("\n" + "="*60)
    print("TEST SUMMARY REPORT")
    print("="*60)
    
    passed_count = sum(1 for v in results.values() if v)
    failed_count = len(results) - passed_count
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\nTotal Tests: {total_count}")
    print(f"Passed: {passed_count} ✅")
    print(f"Failed: {failed_count} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if failed_count > 0:
        print("\n❌ Failed Tests:")
        for test_name, passed in results.items():
            if not passed:
                print(f"  - {test_name}")
                if test_name in errors:
                    print(f"    Error: {errors[test_name]}")
    
    print("\n" + "="*60)
    
    # Determine overall status
    if pass_rate == 100:
        print("🎉 ALL TESTS PASSED! The implementation is working correctly.")
    elif pass_rate >= 80:
        print("✅ Most tests passed. Minor issues to address.")
    elif pass_rate >= 60:
        print("⚠️ Some tests failed. Review and fix issues.")
    else:
        print("❌ Many tests failed. Significant issues to resolve.")
    
    print("="*60)
    
    # Return exit code
    return 0 if pass_rate == 100 else 1

if __name__ == "__main__":
    sys.exit(main())