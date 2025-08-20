from flask import Flask, render_template, request, jsonify, send_file
import json
import time
from datetime import datetime
import os
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops (needed for Vercel)
nest_asyncio.apply()

# Import services - using real implementations
from services.hunter_service import HunterService
from services.job_scraper import JobScraper
from services.news_collector import NewsCollector
from services.website_scraper import WebsiteScraper
from services.company_resolver import CompanyResolver
from scoring.readiness_scorer import ReadinessScorer
from scoring.recommendation_engine import RecommendationEngine
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Disable caching in development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Add cache control headers
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    return response

# Initialize services
hunter_service = HunterService(os.getenv('HUNTER_API_KEY'))
job_scraper = JobScraper()
news_collector = NewsCollector(Config.NEWS_API_KEY)
website_scraper = WebsiteScraper()
company_resolver = CompanyResolver()
readiness_scorer = ReadinessScorer()
recommendation_engine = RecommendationEngine()

@app.route('/')
def index():
    """Render the main dashboard"""
    # Add timestamp for cache busting
    version = int(time.time())
    return render_template('index.html', version=version)

@app.route('/api/company-suggestions', methods=['GET'])
def get_company_suggestions():
    """Get company name suggestions for autocomplete - now with alias support"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    # Use company resolver to find similar companies including aliases
    similar_companies = company_resolver.find_similar_companies(query, limit=10)
    
    # Format suggestions for the frontend
    suggestions = []
    seen_names = set()  # Avoid duplicates
    
    for company in similar_companies:
        name = company['name']
        if name not in seen_names:
            seen_names.add(name)
            suggestion = {
                'name': name,
                'type': company.get('type', 'Financial Services'),
                'sector': company.get('sector', 'Finance'),
                'ticker': company.get('ticker'),
                'match_type': company.get('match_type', 'fuzzy')
            }
            
            # Add display text to show what matched (e.g., "JPMorgan Chase (JPM)")
            if company.get('ticker') and query.upper() == company.get('ticker'):
                suggestion['display'] = f"{name} ({company.get('ticker')})"
            elif company.get('match_type') == 'alias':
                suggestion['display'] = name
                # Show that it matched an alias
                if query.lower() != name.lower():
                    suggestion['hint'] = f"Matched: {query}"
            else:
                suggestion['display'] = name
            
            suggestions.append(suggestion)
    
    # If still no suggestions and query looks like a ticker, try ticker search
    if not suggestions and len(query) <= 5 and query.isalpha():
        ticker_result = company_resolver.search_by_ticker(query)
        if ticker_result:
            suggestions.append({
                'name': ticker_result['canonical'],
                'type': ticker_result.get('type', 'Financial Services'),
                'sector': ticker_result.get('sector', 'Finance'),
                'ticker': ticker_result.get('ticker'),
                'display': f"{ticker_result['canonical']} ({ticker_result.get('ticker')})",
                'match_type': 'ticker'
            })
    
    return jsonify({'suggestions': suggestions})

@app.route('/api/validate-company', methods=['GET'])
def validate_company():
    """Validate if a company name exists in our database"""
    company_name = request.args.get('name', '').strip()
    
    if not company_name:
        return jsonify({'valid': False, 'message': 'Company name is required'})
    
    # Load finance companies data
    companies_file = os.path.join(app.static_folder, 'data', 'finance_companies.json')
    
    try:
        with open(companies_file, 'r') as f:
            companies_data = json.load(f)
            companies = companies_data.get('companies', [])
    except (FileNotFoundError, json.JSONDecodeError):
        companies = []
    
    # Check for exact match (case-insensitive)
    company_name_lower = company_name.lower()
    exact_match = False
    suggestions = []
    
    for company in companies:
        if company['name'].lower() == company_name_lower:
            exact_match = True
            break
        # Collect potential suggestions for partial matches
        elif company_name_lower in company['name'].lower() or any(word.startswith(company_name_lower.split()[0] if company_name_lower.split() else '') for word in company['name'].lower().split()):
            suggestions.append(company['name'])
            if len(suggestions) >= 3:
                break
    
    if exact_match:
        return jsonify({
            'valid': True,
            'message': 'Company found in database'
        })
    else:
        return jsonify({
            'valid': False,
            'message': f"Company '{company_name}' not found in database",
            'suggestions': suggestions[:3]
        })

@app.route('/analyze', methods=['POST'])
@app.route('/analyze/comprehensive', methods=['POST'])
def analyze_company():
    """Main endpoint for company analysis"""
    try:
        data = request.json
        # Support both 'company_name' and 'name' parameters
        company_name = data.get('company_name') or data.get('name', '')
        company_name = company_name.strip()
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Initialize response
        response = {
            'company_name': company_name,
            'status': 'processing',
            'steps': []
        }
        
        # Step 1: Resolve company name and get domain
        resolved_company = company_resolver.resolve_company(company_name)
        canonical_name = resolved_company.get('canonical', company_name)
        domain = resolved_company.get('domain')
        ticker = resolved_company.get('ticker')
        
        # If no domain found, try to construct one
        if not domain:
            domain = f"{company_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com"
        
        # Step 2: Company Enrichment using Hunter.io
        response['steps'].append({'step': 'Fetching company information', 'status': 'complete'})
        
        # Run async Hunter.io search with resolved domain
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        hunter_data = loop.run_until_complete(hunter_service.search_domain(domain))
        
        # Convert Hunter data to expected format
        if hunter_data:
            company_info = {
                'name': hunter_data.company_name or canonical_name,
                'domain': hunter_data.domain or domain,
                'industry': hunter_data.company_industry or 'Financial Services',
                'employeeCount': 0,  # Hunter doesn't provide this directly
                'description': f"{hunter_data.company_name or canonical_name} - {hunter_data.company_type or 'Company'}",
                'tags': hunter_data.technologies or [],
                'techStack': hunter_data.technologies or [],
                'ticker': ticker,  # Add ticker from resolver
                'location': {
                    'city': hunter_data.city or 'New York',
                    'state': hunter_data.state or 'NY',
                    'country': hunter_data.country or 'US'
                },
                'social': {
                    'twitter': hunter_data.twitter,
                    'facebook': hunter_data.facebook,
                    'linkedin': hunter_data.linkedin
                },
                'email_count': hunter_data.email_count
            }
        else:
            # Fallback if Hunter.io fails
            company_info = {
                'name': canonical_name,
                'domain': domain,
                'industry': 'Financial Services',
                'employeeCount': 0,
                'description': f"{canonical_name} company information",
                'tags': [],
                'techStack': [],
                'ticker': ticker,  # Add ticker from resolver
                'location': {
                    'city': 'New York',
                    'state': 'NY',
                    'country': 'US'
                }
            }
        
        # Step 3: Job Analysis (use canonical name for better search results)
        response['steps'].append({'step': 'Analyzing job postings', 'status': 'complete'})
        job_analysis = job_scraper.analyze_job_postings(canonical_name)
        
        # Step 4: News Analysis (use canonical name for better search results)
        response['steps'].append({'step': 'Collecting recent news', 'status': 'complete'})
        news_analysis = news_collector.get_recent_news(canonical_name)
        
        # Step 4: Website Analysis
        response['steps'].append({'step': 'Analyzing company website', 'status': 'complete'})
        domain = company_info.get('domain', f"{company_name.lower().replace(' ', '')}.com")
        website_analysis = website_scraper.analyze_website(domain)
        
        # Compile all data
        company_data = {
            'company_info': company_info,
            'job_analysis': job_analysis,
            'news_analysis': news_analysis,
            'website_analysis': website_analysis
        }
        
        # Step 5: Calculate AI Readiness Score
        response['steps'].append({'step': 'Calculating AI readiness score', 'status': 'complete'})
        readiness_score = readiness_scorer.calculate_ai_readiness_score(company_data)
        
        # Step 6: Generate Recommendations
        response['steps'].append({'step': 'Generating sales recommendations', 'status': 'complete'})
        recommendations = recommendation_engine.generate_sales_approach(company_data, readiness_score)
        
        # Compile final response (matching JavaScript expectations)
        response['status'] = 'complete'
        response['company_name'] = company_name
        response['company_info'] = company_info
        response['readiness_score'] = readiness_score
        response['ai_readiness_score'] = readiness_score.get('total_score', 0)
        response['readiness_category'] = readiness_score.get('readiness_level', 'Unknown')
        response['component_scores'] = readiness_score.get('component_scores', {})
        response['recommendations'] = recommendations
        response['job_analysis'] = job_analysis
        response['news_analysis'] = news_analysis
        response['website_analysis'] = website_analysis
        response['company_data'] = {
            'basic_info': company_info,
            'job_postings': job_analysis,
            'news_insights': news_analysis,
            'tech_signals': website_analysis
        }
        response['domain'] = company_info.get('domain', '')
        response['timestamp'] = datetime.now().isoformat()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """Generate PDF report for analysis"""
    try:
        request_data = request.json
        company_name = request_data.get('name', '')
        
        # Check if we have the full analysis data
        if 'company_name' in request_data and 'readiness_score' in request_data:
            # Full data provided
            data = request_data
        else:
            # Need to re-analyze the company
            # Resolve company name first
            resolved_company = company_resolver.resolve_company(company_name)
            canonical_name = resolved_company.get('canonical', company_name)
            domain = resolved_company.get('domain') or request_data.get('domain', f"{company_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com")
            
            # Get Hunter.io data
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            hunter_data = loop.run_until_complete(hunter_service.search_domain(domain))
            
            # Convert Hunter data to expected format
            if hunter_data:
                company_info = {
                    'name': hunter_data.company_name or company_name,
                    'domain': hunter_data.domain or domain,
                    'industry': hunter_data.company_industry or 'Financial Services',
                    'employeeCount': 0,
                    'description': f"{hunter_data.company_name or company_name} - {hunter_data.company_type or 'Company'}",
                    'tags': hunter_data.technologies or [],
                    'techStack': hunter_data.technologies or [],
                    'location': {
                        'city': hunter_data.city or 'New York',
                        'state': hunter_data.state or 'NY',
                        'country': hunter_data.country or 'US'
                    }
                }
            else:
                company_info = {
                    'name': company_name,
                    'domain': domain,
                    'industry': 'Financial Services',
                    'employeeCount': 0,
                    'description': f"{company_name} company information",
                    'tags': [],
                    'techStack': [],
                    'location': {'city': 'New York', 'state': 'NY', 'country': 'US'}
                }
            
            company_data = {
                'company_info': company_info,
                'job_analysis': job_scraper.analyze_job_postings(company_name),
                'news_analysis': news_collector.get_recent_news(company_name),
                'website_analysis': website_scraper.analyze_website(domain)
            }
            
            readiness_score = readiness_scorer.calculate_ai_readiness_score(company_data)
            recommendations = recommendation_engine.generate_sales_approach(company_data, readiness_score)
            
            data = {
                'company_name': company_name,
                'company_info': company_data['company_info'],
                'readiness_score': readiness_score,
                'recommendations': recommendations,
                'job_analysis': company_data['job_analysis'],
                'news_analysis': company_data['news_analysis'],
                'website_analysis': company_data['website_analysis'],
                'timestamp': datetime.now().isoformat()
            }
        
        # Import enhanced PDF generator
        from services.enhanced_report_generator import EnhancedPDFReportGenerator
        import os
        import shutil
        
        # Use /tmp directory on Vercel and copy logo
        if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            output_dir = "/tmp/reports"
            
            # Copy logo to /tmp for Vercel if it doesn't exist
            if not os.path.exists("/tmp/modelml.png"):
                logo_source = os.path.join(os.path.dirname(__file__), "static", "modelml.png")
                if os.path.exists(logo_source):
                    shutil.copy(logo_source, "/tmp/modelml.png")
        else:
            output_dir = "reports"
        
        # Create enhanced PDF generator
        pdf_gen = EnhancedPDFReportGenerator(output_dir=output_dir)
        
        # Ensure data has the correct structure for enhanced generator
        # Extract the numeric score from readiness_score if it's a dict
        readiness_score_value = data.get('readiness_score', {})
        if isinstance(readiness_score_value, dict):
            ai_score = readiness_score_value.get('total_score', 0)
        else:
            ai_score = data.get('ai_readiness_score', 0)
        
        enhanced_data = {
            'company_name': data.get('company_name', company_name),
            'ai_readiness_score': ai_score,
            'readiness_category': data.get('readiness_category', readiness_score_value.get('readiness_level', 'Assessment Pending') if isinstance(readiness_score_value, dict) else 'Assessment Pending'),
            'confidence': data.get('confidence', 0.85),
            'component_scores': data.get('component_scores', readiness_score_value.get('component_scores', {}) if isinstance(readiness_score_value, dict) else {}),
            'data_sources': data.get('data_sources', {}),
            'company_data': data.get('company_data', {}),
            'is_financial_company': data.get('is_financial_company', False),
            'recommendations': data.get('recommendations', {}),
            'news_analysis': data.get('news_analysis', {}),
            'decision_makers': data.get('decision_makers', [])
        }
        
        pdf_path = pdf_gen.generate_report(
            company_name=enhanced_data['company_name'],
            ai_readiness_data=enhanced_data
        )
        
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f"{company_name}_AI_Readiness_Report.pdf")
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test_companies')
def test_companies():
    """Endpoint to get test company suggestions"""
    test_companies = [
        {'name': 'JPMorgan Chase', 'expected': 'Very High'},
        {'name': 'Goldman Sachs', 'expected': 'High'},
        {'name': 'BlackRock', 'expected': 'High'}
    ]
    return jsonify(test_companies)

if __name__ == '__main__':
    app.run(debug=True, port=8000)