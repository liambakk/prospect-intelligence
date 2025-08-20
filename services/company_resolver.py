"""
Company Resolver Service
Handles company name resolution, alias mapping, and domain lookup
"""

import json
import os
import re
import requests
from typing import Dict, Optional, List, Tuple
from difflib import get_close_matches


class CompanyResolver:
    def __init__(self):
        """Initialize the company resolver with mappings and company data"""
        self.mappings = {}
        self.companies = []
        self.load_data()
        
    def load_data(self):
        """Load company mappings and finance companies data"""
        # Load company mappings
        mappings_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'data', 'company_mappings.json'
        )
        
        try:
            with open(mappings_path, 'r') as f:
                data = json.load(f)
                self.mappings = data.get('mappings', {})
        except (FileNotFoundError, json.JSONDecodeError):
            print("Warning: Could not load company mappings")
            self.mappings = {}
        
        # Load finance companies data
        companies_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'data', 'finance_companies.json'
        )
        
        try:
            with open(companies_path, 'r') as f:
                data = json.load(f)
                self.companies = data.get('companies', [])
        except (FileNotFoundError, json.JSONDecodeError):
            print("Warning: Could not load finance companies")
            self.companies = []
    
    def resolve_company(self, input_name: str) -> Dict[str, Optional[str]]:
        """
        Resolve a company name to its canonical form and domain
        
        Args:
            input_name: The user's input company name
            
        Returns:
            Dictionary with canonical name, domain, and ticker
        """
        if not input_name:
            return {'canonical': None, 'domain': None, 'ticker': None}
        
        # Clean and normalize the input
        normalized = input_name.strip().lower()
        
        # First, check direct mapping
        if normalized in self.mappings:
            mapping = self.mappings[normalized]
            return {
                'canonical': mapping.get('canonical'),
                'domain': mapping.get('domain'),
                'ticker': mapping.get('ticker')
            }
        
        # Check if it's already a canonical name in our companies list
        for company in self.companies:
            if company['name'].lower() == normalized:
                # Try to find domain in mappings
                domain = self._get_domain_for_canonical(company['name'])
                return {
                    'canonical': company['name'],
                    'domain': domain,
                    'ticker': company.get('ticker')
                }
        
        # Try fuzzy matching
        similar = self.find_similar_companies(input_name)
        if similar:
            best_match = similar[0]
            return {
                'canonical': best_match['name'],
                'domain': best_match.get('domain'),
                'ticker': best_match.get('ticker')
            }
        
        # If no match found, try to construct a reasonable domain
        # This is a fallback for companies not in our database
        domain = self._construct_domain(input_name)
        return {
            'canonical': input_name,  # Use original input as canonical
            'domain': domain,
            'ticker': None
        }
    
    def _get_domain_for_canonical(self, canonical_name: str) -> Optional[str]:
        """Get domain for a canonical company name"""
        # Search through mappings for this canonical name
        for mapping in self.mappings.values():
            if mapping.get('canonical') == canonical_name:
                return mapping.get('domain')
        
        # If not found, try to construct domain
        return self._construct_domain(canonical_name)
    
    def _construct_domain(self, company_name: str) -> str:
        """Construct a likely domain from company name"""
        # Remove common suffixes
        name = re.sub(r'\b(inc|incorporated|corp|corporation|llc|ltd|limited|plc|group|holdings?|partners?)\b', 
                     '', company_name, flags=re.IGNORECASE)
        
        # Clean and format
        name = re.sub(r'[^\w\s]', '', name)  # Remove special characters
        name = name.strip().lower()
        name = re.sub(r'\s+', '', name)  # Remove spaces
        
        # Add .com
        return f"{name}.com" if name else None
    
    def find_similar_companies(self, input_name: str, limit: int = 5) -> List[Dict]:
        """
        Find similar companies using fuzzy matching
        
        Args:
            input_name: User's input
            limit: Maximum number of suggestions
            
        Returns:
            List of similar companies with their details
        """
        input_lower = input_name.lower().strip()
        results = []
        
        # Check partial matches in mappings
        for key, mapping in self.mappings.items():
            if input_lower in key or key in input_lower:
                canonical = mapping.get('canonical')
                # Find full company info
                for company in self.companies:
                    if company['name'] == canonical:
                        results.append({
                            'name': canonical,
                            'domain': mapping.get('domain'),
                            'ticker': mapping.get('ticker'),
                            'type': company.get('type'),
                            'sector': company.get('sector'),
                            'match_type': 'alias'
                        })
                        break
                else:
                    # Company not in our list, but in mappings
                    results.append({
                        'name': canonical,
                        'domain': mapping.get('domain'),
                        'ticker': mapping.get('ticker'),
                        'match_type': 'alias'
                    })
        
        # Check aliases within mappings
        for mapping in self.mappings.values():
            aliases = mapping.get('aliases', [])
            for alias in aliases:
                if input_lower in alias.lower() or alias.lower() in input_lower:
                    canonical = mapping.get('canonical')
                    if not any(r['name'] == canonical for r in results):
                        # Find full company info
                        for company in self.companies:
                            if company['name'] == canonical:
                                results.append({
                                    'name': canonical,
                                    'domain': mapping.get('domain'),
                                    'ticker': mapping.get('ticker'),
                                    'type': company.get('type'),
                                    'sector': company.get('sector'),
                                    'match_type': 'alias'
                                })
                                break
        
        # Check direct company names
        for company in self.companies:
            if input_lower in company['name'].lower():
                if not any(r['name'] == company['name'] for r in results):
                    domain = self._get_domain_for_canonical(company['name'])
                    results.append({
                        'name': company['name'],
                        'domain': domain,
                        'ticker': company.get('ticker'),
                        'type': company.get('type'),
                        'sector': company.get('sector'),
                        'match_type': 'partial'
                    })
        
        # Use difflib for close matches
        all_names = [c['name'] for c in self.companies]
        close_matches = get_close_matches(input_name, all_names, n=limit, cutoff=0.6)
        
        for match in close_matches:
            if not any(r['name'] == match for r in results):
                for company in self.companies:
                    if company['name'] == match:
                        domain = self._get_domain_for_canonical(match)
                        results.append({
                            'name': match,
                            'domain': domain,
                            'ticker': company.get('ticker'),
                            'type': company.get('type'),
                            'sector': company.get('sector'),
                            'match_type': 'fuzzy'
                        })
                        break
        
        # Sort by match quality (alias > partial > fuzzy)
        match_priority = {'alias': 0, 'partial': 1, 'fuzzy': 2}
        results.sort(key=lambda x: match_priority.get(x.get('match_type', 'fuzzy'), 3))
        
        return results[:limit]
    
    def get_domain_for_company(self, company_name: str) -> Optional[str]:
        """
        Get the domain for a company name
        
        Args:
            company_name: Company name to lookup
            
        Returns:
            Domain name or None
        """
        resolved = self.resolve_company(company_name)
        return resolved.get('domain')
    
    def search_by_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Search for a company by ticker symbol
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Company information or None
        """
        ticker_upper = ticker.upper().strip()
        
        # Check mappings first
        for mapping in self.mappings.values():
            if mapping.get('ticker') == ticker_upper:
                return {
                    'canonical': mapping.get('canonical'),
                    'domain': mapping.get('domain'),
                    'ticker': ticker_upper
                }
        
        # Check companies list
        for company in self.companies:
            if company.get('ticker') == ticker_upper:
                domain = self._get_domain_for_canonical(company['name'])
                return {
                    'canonical': company['name'],
                    'domain': domain,
                    'ticker': ticker_upper,
                    'type': company.get('type'),
                    'sector': company.get('sector')
                }
        
        return None
    
    def try_clearbit_lookup(self, company_name: str) -> Optional[Dict]:
        """
        Try to resolve company using Clearbit Name-to-Domain API
        Free tier: 50k requests/month
        
        Args:
            company_name: Company name to lookup
            
        Returns:
            Company information from Clearbit or None
        """
        # Note: Clearbit API requires authentication
        # This is a placeholder for when API key is configured
        try:
            # Clearbit Name to Domain API endpoint
            url = "https://company.clearbit.com/v1/domains/find"
            params = {"name": company_name}
            
            # Note: Need to add Clearbit API key to headers
            # headers = {"Authorization": f"Bearer {CLEARBIT_API_KEY}"}
            # response = requests.get(url, params=params, headers=headers, timeout=5)
            
            # For now, return None as we don't have Clearbit configured
            return None
            
        except Exception as e:
            print(f"Clearbit lookup failed: {e}")
            return None