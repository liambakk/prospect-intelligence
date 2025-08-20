"""
Company Database Service for autocomplete suggestions
Provides a curated list of companies with focus on financial services
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CompanyDatabase:
    """
    Provides company suggestions for autocomplete
    Focus on financial services companies that ModelML targets
    """
    
    def __init__(self):
        """Initialize with a curated list of companies"""
        self.companies = self._initialize_company_list()
        logger.info(f"CompanyDatabase initialized with {len(self.companies)} companies")
    
    def _initialize_company_list(self) -> List[Dict[str, str]]:
        """
        Initialize the company database with major companies
        Focused on financial services but includes other sectors
        """
        return [
            # Major Banks
            {"name": "JPMorgan Chase", "ticker": "JPM", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "Bank of America", "ticker": "BAC", "type": "Commercial Bank", "sector": "Financial Services"},
            {"name": "Wells Fargo", "ticker": "WFC", "type": "Commercial Bank", "sector": "Financial Services"},
            {"name": "Goldman Sachs", "ticker": "GS", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "Morgan Stanley", "ticker": "MS", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "Citigroup", "ticker": "C", "type": "Commercial Bank", "sector": "Financial Services"},
            {"name": "Deutsche Bank", "ticker": "DB", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "Barclays", "ticker": "BCS", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "Credit Suisse", "ticker": "CS", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "UBS", "ticker": "UBS", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "HSBC", "ticker": "HSBC", "type": "Commercial Bank", "sector": "Financial Services"},
            {"name": "BNP Paribas", "ticker": "BNP", "type": "Investment Bank", "sector": "Financial Services"},
            {"name": "Intesa Sanpaolo", "ticker": "ISP.MI", "type": "Commercial Bank", "sector": "Financial Services"},
            {"name": "Royal Bank of Canada", "ticker": "RY", "type": "Commercial Bank", "sector": "Financial Services"},
            {"name": "TD Bank", "ticker": "TD", "type": "Commercial Bank", "sector": "Financial Services"},
            {"name": "PNC Financial", "ticker": "PNC", "type": "Regional Bank", "sector": "Financial Services"},
            {"name": "Truist Financial", "ticker": "TFC", "type": "Regional Bank", "sector": "Financial Services"},
            {"name": "U.S. Bancorp", "ticker": "USB", "type": "Regional Bank", "sector": "Financial Services"},
            
            # Asset Management
            {"name": "BlackRock", "ticker": "BLK", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "Vanguard Group", "ticker": "", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "Fidelity Investments", "ticker": "", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "State Street", "ticker": "STT", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "Charles Schwab", "ticker": "SCHW", "type": "Brokerage", "sector": "Financial Services"},
            {"name": "T. Rowe Price", "ticker": "TROW", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "Franklin Templeton", "ticker": "BEN", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "Invesco", "ticker": "IVZ", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "Northern Trust", "ticker": "NTRS", "type": "Asset Manager", "sector": "Financial Services"},
            {"name": "AllianceBernstein", "ticker": "AB", "type": "Asset Manager", "sector": "Financial Services"},
            
            # Insurance Companies
            {"name": "Berkshire Hathaway", "ticker": "BRK.B", "type": "Insurance", "sector": "Financial Services"},
            {"name": "AIG", "ticker": "AIG", "type": "Insurance", "sector": "Financial Services"},
            {"name": "MetLife", "ticker": "MET", "type": "Insurance", "sector": "Financial Services"},
            {"name": "Prudential Financial", "ticker": "PRU", "type": "Insurance", "sector": "Financial Services"},
            {"name": "Chubb", "ticker": "CB", "type": "Insurance", "sector": "Financial Services"},
            {"name": "Progressive", "ticker": "PGR", "type": "Insurance", "sector": "Financial Services"},
            {"name": "Allstate", "ticker": "ALL", "type": "Insurance", "sector": "Financial Services"},
            {"name": "Travelers", "ticker": "TRV", "type": "Insurance", "sector": "Financial Services"},
            {"name": "Hartford Financial", "ticker": "HIG", "type": "Insurance", "sector": "Financial Services"},
            {"name": "Aflac", "ticker": "AFL", "type": "Insurance", "sector": "Financial Services"},
            
            # Hedge Funds & PE
            {"name": "Bridgewater Associates", "ticker": "", "type": "Hedge Fund", "sector": "Financial Services"},
            {"name": "Renaissance Technologies", "ticker": "", "type": "Hedge Fund", "sector": "Financial Services"},
            {"name": "Two Sigma", "ticker": "", "type": "Hedge Fund", "sector": "Financial Services"},
            {"name": "Citadel", "ticker": "", "type": "Hedge Fund", "sector": "Financial Services"},
            {"name": "D.E. Shaw", "ticker": "", "type": "Hedge Fund", "sector": "Financial Services"},
            {"name": "Millennium Management", "ticker": "", "type": "Hedge Fund", "sector": "Financial Services"},
            {"name": "Elliott Management", "ticker": "", "type": "Hedge Fund", "sector": "Financial Services"},
            {"name": "Blackstone", "ticker": "BX", "type": "Private Equity", "sector": "Financial Services"},
            {"name": "KKR", "ticker": "KKR", "type": "Private Equity", "sector": "Financial Services"},
            {"name": "Apollo Global", "ticker": "APO", "type": "Private Equity", "sector": "Financial Services"},
            {"name": "Carlyle Group", "ticker": "CG", "type": "Private Equity", "sector": "Financial Services"},
            {"name": "Sequoia Capital", "ticker": "", "type": "Venture Capital", "sector": "Financial Services"},
            {"name": "Andreessen Horowitz", "ticker": "", "type": "Venture Capital", "sector": "Financial Services"},
            
            # Fintech Companies
            {"name": "PayPal", "ticker": "PYPL", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Square", "ticker": "SQ", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Stripe", "ticker": "", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Plaid", "ticker": "", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Robinhood", "ticker": "HOOD", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Coinbase", "ticker": "COIN", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Affirm", "ticker": "AFRM", "type": "Fintech", "sector": "Financial Services"},
            {"name": "SoFi", "ticker": "SOFI", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Klarna", "ticker": "", "type": "Fintech", "sector": "Financial Services"},
            {"name": "Chime", "ticker": "", "type": "Fintech", "sector": "Financial Services"},
            
            # Credit Card Companies
            {"name": "Visa", "ticker": "V", "type": "Payment Processor", "sector": "Financial Services"},
            {"name": "Mastercard", "ticker": "MA", "type": "Payment Processor", "sector": "Financial Services"},
            {"name": "American Express", "ticker": "AXP", "type": "Credit Card", "sector": "Financial Services"},
            {"name": "Discover Financial", "ticker": "DFS", "type": "Credit Card", "sector": "Financial Services"},
            {"name": "Capital One", "ticker": "COF", "type": "Credit Card", "sector": "Financial Services"},
            {"name": "Synchrony Financial", "ticker": "SYF", "type": "Credit Card", "sector": "Financial Services"},
            
            # Exchanges & Market Infrastructure
            {"name": "NYSE", "ticker": "ICE", "type": "Exchange", "sector": "Financial Services"},
            {"name": "Nasdaq", "ticker": "NDAQ", "type": "Exchange", "sector": "Financial Services"},
            {"name": "CME Group", "ticker": "CME", "type": "Exchange", "sector": "Financial Services"},
            {"name": "Intercontinental Exchange", "ticker": "ICE", "type": "Exchange", "sector": "Financial Services"},
            {"name": "CBOE Global Markets", "ticker": "CBOE", "type": "Exchange", "sector": "Financial Services"},
            
            # Rating Agencies & Data Providers
            {"name": "S&P Global", "ticker": "SPGI", "type": "Rating Agency", "sector": "Financial Services"},
            {"name": "Moody's", "ticker": "MCO", "type": "Rating Agency", "sector": "Financial Services"},
            {"name": "Fitch Ratings", "ticker": "", "type": "Rating Agency", "sector": "Financial Services"},
            {"name": "MSCI", "ticker": "MSCI", "type": "Data Provider", "sector": "Financial Services"},
            {"name": "FactSet", "ticker": "FDS", "type": "Data Provider", "sector": "Financial Services"},
            {"name": "Bloomberg", "ticker": "", "type": "Data Provider", "sector": "Financial Services"},
            {"name": "Refinitiv", "ticker": "", "type": "Data Provider", "sector": "Financial Services"},
            
            # Major Tech Companies (for comparison)
            {"name": "Apple", "ticker": "AAPL", "type": "Technology", "sector": "Technology"},
            {"name": "Microsoft", "ticker": "MSFT", "type": "Technology", "sector": "Technology"},
            {"name": "Google", "ticker": "GOOGL", "type": "Technology", "sector": "Technology"},
            {"name": "Amazon", "ticker": "AMZN", "type": "E-commerce", "sector": "Technology"},
            {"name": "Meta", "ticker": "META", "type": "Social Media", "sector": "Technology"},
            {"name": "Tesla", "ticker": "TSLA", "type": "Automotive", "sector": "Technology"},
            {"name": "NVIDIA", "ticker": "NVDA", "type": "Semiconductors", "sector": "Technology"},
            {"name": "Oracle", "ticker": "ORCL", "type": "Enterprise Software", "sector": "Technology"},
            {"name": "Salesforce", "ticker": "CRM", "type": "Enterprise Software", "sector": "Technology"},
            {"name": "IBM", "ticker": "IBM", "type": "Technology", "sector": "Technology"},
            {"name": "Intel", "ticker": "INTC", "type": "Semiconductors", "sector": "Technology"},
            {"name": "AMD", "ticker": "AMD", "type": "Semiconductors", "sector": "Technology"},
            {"name": "Netflix", "ticker": "NFLX", "type": "Entertainment", "sector": "Technology"},
            {"name": "Uber", "ticker": "UBER", "type": "Transportation", "sector": "Technology"},
            {"name": "Airbnb", "ticker": "ABNB", "type": "Travel", "sector": "Technology"},
            {"name": "Spotify", "ticker": "SPOT", "type": "Entertainment", "sector": "Technology"},
            {"name": "Palantir", "ticker": "PLTR", "type": "Data Analytics", "sector": "Technology"},
            {"name": "Snowflake", "ticker": "SNOW", "type": "Cloud Data", "sector": "Technology"},
            {"name": "Databricks", "ticker": "", "type": "Data Analytics", "sector": "Technology"},
            {"name": "OpenAI", "ticker": "", "type": "AI", "sector": "Technology"},
            
            # Healthcare & Pharma
            {"name": "Johnson & Johnson", "ticker": "JNJ", "type": "Healthcare", "sector": "Healthcare"},
            {"name": "UnitedHealth Group", "ticker": "UNH", "type": "Health Insurance", "sector": "Healthcare"},
            {"name": "Pfizer", "ticker": "PFE", "type": "Pharmaceutical", "sector": "Healthcare"},
            {"name": "CVS Health", "ticker": "CVS", "type": "Healthcare", "sector": "Healthcare"},
            
            # Retail & Consumer
            {"name": "Walmart", "ticker": "WMT", "type": "Retail", "sector": "Consumer"},
            {"name": "Target", "ticker": "TGT", "type": "Retail", "sector": "Consumer"},
            {"name": "Home Depot", "ticker": "HD", "type": "Retail", "sector": "Consumer"},
            {"name": "Costco", "ticker": "COST", "type": "Retail", "sector": "Consumer"},
            {"name": "Starbucks", "ticker": "SBUX", "type": "Restaurant", "sector": "Consumer"},
            {"name": "McDonald's", "ticker": "MCD", "type": "Restaurant", "sector": "Consumer"},
            {"name": "Nike", "ticker": "NKE", "type": "Apparel", "sector": "Consumer"},
            {"name": "Coca-Cola", "ticker": "KO", "type": "Beverage", "sector": "Consumer"},
            {"name": "Procter & Gamble", "ticker": "PG", "type": "Consumer Goods", "sector": "Consumer"},
            
            # Energy & Utilities
            {"name": "ExxonMobil", "ticker": "XOM", "type": "Energy", "sector": "Energy"},
            {"name": "Chevron", "ticker": "CVX", "type": "Energy", "sector": "Energy"},
            {"name": "Shell", "ticker": "SHEL", "type": "Energy", "sector": "Energy"},
            {"name": "BP", "ticker": "BP", "type": "Energy", "sector": "Energy"},
            
            # Airlines & Transportation
            {"name": "Delta Air Lines", "ticker": "DAL", "type": "Airline", "sector": "Transportation"},
            {"name": "United Airlines", "ticker": "UAL", "type": "Airline", "sector": "Transportation"},
            {"name": "American Airlines", "ticker": "AAL", "type": "Airline", "sector": "Transportation"},
            {"name": "Southwest Airlines", "ticker": "LUV", "type": "Airline", "sector": "Transportation"},
            {"name": "FedEx", "ticker": "FDX", "type": "Logistics", "sector": "Transportation"},
            {"name": "UPS", "ticker": "UPS", "type": "Logistics", "sector": "Transportation"},
        ]
    
    def search_companies(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for companies matching the query
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching companies with their details
        """
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        matches = []
        
        # Score each company based on match quality
        for company in self.companies:
            name_lower = company["name"].lower()
            ticker_lower = company.get("ticker", "").lower()
            
            # Exact match gets highest priority
            if name_lower == query_lower or ticker_lower == query_lower:
                score = 100
            # Starts with query gets high priority
            elif name_lower.startswith(query_lower) or ticker_lower.startswith(query_lower):
                score = 90
            # Word boundary match (e.g., "Chase" in "JPMorgan Chase")
            elif any(word.startswith(query_lower) for word in name_lower.split()):
                score = 80
            # Contains query anywhere
            elif query_lower in name_lower or query_lower in ticker_lower:
                score = 70
            # Fuzzy match for typos (simple approach)
            elif self._fuzzy_match(query_lower, name_lower):
                score = 60
            else:
                continue
            
            matches.append({
                "company": company,
                "score": score
            })
        
        # Sort by score (highest first) and then by name
        matches.sort(key=lambda x: (-x["score"], x["company"]["name"]))
        
        # Return top matches
        return [match["company"] for match in matches[:limit]]
    
    def _fuzzy_match(self, query: str, target: str, max_distance: int = 2) -> bool:
        """
        Simple fuzzy matching for typos
        Returns True if query is within max_distance edits of any word in target
        """
        # For performance, only check if query is reasonably short
        if len(query) > 10:
            return False
        
        target_words = target.split()
        for word in target_words:
            if self._levenshtein_distance(query, word.lower()) <= max_distance:
                return True
        return False
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # j+1 instead of j since previous_row and current_row are one character longer
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_company_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get company details by exact name match
        
        Args:
            name: Company name to search for
            
        Returns:
            Company details if found, None otherwise
        """
        name_lower = name.lower()
        for company in self.companies:
            if company["name"].lower() == name_lower:
                return company
        return None
    
    def get_financial_companies(self) -> List[Dict[str, str]]:
        """
        Get all financial services companies
        
        Returns:
            List of financial services companies
        """
        return [c for c in self.companies if c.get("sector") == "Financial Services"]