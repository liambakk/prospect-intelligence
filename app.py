from flask import Flask, render_template, request, jsonify, send_file
import json
import time
from datetime import datetime
import os

# Import services
from services.clearbit_service import ClearbitService
from services.job_scraper import JobScraper
from services.news_collector import NewsCollector
from services.website_scraper import WebsiteScraper
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
clearbit_service = ClearbitService(Config.CLEARBIT_API_KEY)
job_scraper = JobScraper()
news_collector = NewsCollector(Config.NEWS_API_KEY)
website_scraper = WebsiteScraper()
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
    """Get company name suggestions for autocomplete"""
    query = request.args.get('q', '').strip().lower()
    
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    # Load finance companies data
    companies_file = os.path.join(app.static_folder, 'data', 'finance_companies.json')
    
    try:
        with open(companies_file, 'r') as f:
            companies_data = json.load(f)
            companies = companies_data.get('companies', [])
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to hardcoded list if file not found
        companies = [
            {"name": "JPMorgan Chase", "type": "Investment Bank", "sector": "Banking"},
            {"name": "Bank of America", "type": "Commercial Bank", "sector": "Banking"},
            {"name": "Goldman Sachs", "type": "Investment Bank", "sector": "Investment Banking"},
            {"name": "Morgan Stanley", "type": "Investment Bank", "sector": "Investment Banking"},
            {"name": "Wells Fargo", "type": "Commercial Bank", "sector": "Banking"}
        ]
    
    # Filter companies based on query
    suggestions = []
    for company in companies:
        company_name_lower = company['name'].lower()
        # Check if query matches start of name or any word in the name
        if (company_name_lower.startswith(query) or 
            any(word.startswith(query) for word in company_name_lower.split())):
            suggestions.append({
                'name': company['name'],
                'type': company.get('type', 'Financial Services'),
                'sector': company.get('sector', 'Finance'),
                'ticker': company.get('ticker')
            })
            
            if len(suggestions) >= 10:  # Limit to 10 suggestions
                break
    
    # If no exact matches, try fuzzy matching
    if not suggestions:
        for company in companies:
            if query in company['name'].lower():
                suggestions.append({
                    'name': company['name'],
                    'type': company.get('type', 'Financial Services'),
                    'sector': company.get('sector', 'Finance'),
                    'ticker': company.get('ticker')
                })
                
                if len(suggestions) >= 10:
                    break
    
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
        
        # Step 1: Company Enrichment
        response['steps'].append({'step': 'Fetching company information', 'status': 'complete'})
        company_info = clearbit_service.enrich_company(company_name)
        
        # Step 2: Job Analysis
        response['steps'].append({'step': 'Analyzing job postings', 'status': 'complete'})
        job_analysis = job_scraper.analyze_job_postings(company_name)
        
        # Step 3: News Analysis
        response['steps'].append({'step': 'Collecting recent news', 'status': 'complete'})
        news_analysis = news_collector.get_recent_news(company_name)
        
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
            # Run the analysis to get fresh data
            company_data = {
                'company_info': clearbit_service.enrich_company(company_name),
                'job_analysis': job_scraper.analyze_job_postings(company_name),
                'news_analysis': news_collector.get_recent_news(company_name),
                'website_analysis': website_scraper.analyze_website(
                    request_data.get('domain', f"{company_name.lower().replace(' ', '')}.com")
                )
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
        
        # Import PDF generator
        from reports.pdf_generator import PDFGenerator
        
        pdf_gen = PDFGenerator()
        pdf_path = pdf_gen.generate_report(data)
        
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