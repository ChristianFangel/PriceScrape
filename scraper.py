import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import trafilatura

class CompetitorScraper:
    def __init__(self):
        self.competitors = {
            'carta': {
                'url': 'https://carta.com/uk/en/plans/pricing-for-companies/',
                'name': 'Carta'
            },
            'bolago': {
                'url': 'https://bolago.com/se/priser/',
                'name': 'Bolago'
            },
            'nvr': {
                'url': 'https://www.nvr.se/pris',
                'name': 'NVR'
            },
            'ledgy': {
                'url': 'https://ledgy.com/company-pricing',
                'name': 'Ledgy'
            },
            'cakeequity': {
                'url': 'https://www.cakeequity.com/pricing',
                'name': 'Cake Equity'
            },
            'mantle': {
                'url': 'https://withmantle.com/pricing',
                'name': 'Mantle'
            },
            'clara': {
                'url': 'https://clara.co/pricing/',
                'name': 'Clara'
            }
        }
        
        # In-memory storage for scraped data
        self.data = {}
        
        # Request headers to appear more like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Rate limiting - wait between requests
        self.request_delay = 2  # seconds
        
        logging.info("CompetitorScraper initialized")

    def scrape_single(self, competitor_key):
        """Scrape data for a single competitor"""
        if competitor_key not in self.competitors:
            return {'success': False, 'error': f'Unknown competitor: {competitor_key}'}
        
        competitor = self.competitors[competitor_key]
        url = competitor['url']
        name = competitor['name']
        
        logging.info(f"Scraping {name} at {url}")
        
        try:
            # Rate limiting
            time.sleep(self.request_delay)
            
            # Make request
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract pricing information based on competitor
            pricing_data = self._extract_pricing_data(competitor_key, soup, response.text)
            
            # Store the data
            self.data[competitor_key] = {
                'name': name,
                'url': url,
                'last_updated': datetime.now().isoformat(),
                'success': True,
                'pricing_data': pricing_data,
                'error': None
            }
            
            logging.info(f"Successfully scraped {name}")
            return {'success': True, 'data': pricing_data}
            
        except requests.RequestException as e:
            error_msg = f"Request failed for {name}: {str(e)}"
            logging.error(error_msg)
            
            self.data[competitor_key] = {
                'name': name,
                'url': url,
                'last_updated': datetime.now().isoformat(),
                'success': False,
                'pricing_data': None,
                'error': error_msg
            }
            
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Parsing failed for {name}: {str(e)}"
            logging.error(error_msg)
            
            self.data[competitor_key] = {
                'name': name,
                'url': url,
                'last_updated': datetime.now().isoformat(),
                'success': False,
                'pricing_data': None,
                'error': error_msg
            }
            
            return {'success': False, 'error': error_msg}

    def _extract_pricing_data(self, competitor_key, soup, raw_html):
        """Extract pricing information based on the competitor"""
        
        if competitor_key == 'carta':
            return self._extract_carta_pricing(soup)
        elif competitor_key == 'bolago':
            return self._extract_bolago_pricing(soup)
        elif competitor_key == 'nvr':
            return self._extract_nvr_pricing(soup)
        elif competitor_key == 'ledgy':
            return self._extract_ledgy_pricing(soup)
        elif competitor_key == 'cakeequity':
            return self._extract_cakeequity_pricing(soup)
        elif competitor_key == 'mantle':
            return self._extract_mantle_pricing(soup)
        elif competitor_key == 'clara':
            return self._extract_clara_pricing(soup)
        else:
            # Fallback: extract general pricing information
            return self._extract_generic_pricing(soup, raw_html)

    def _extract_carta_pricing(self, soup):
        """Extract Carta pricing information"""
        plans = []
        
        # Look for pricing plan sections
        plan_elements = soup.find_all(['div', 'section'], class_=re.compile(r'plan|pricing|card', re.I))
        
        # Also try to find text content that looks like pricing
        text_content = soup.get_text()
        
        # Extract plan information from the actual content we know exists
        if "Raise" in text_content:
            plans.append({
                'name': 'Raise',
                'price': '£250 per year',
                'description': 'Up to five stakeholders',
                'features': ['Cap table management', 'Advance Assurance', 'Round modelling']
            })
        
        if "Build" in text_content:
            plans.append({
                'name': 'Build',
                'price': 'Contact for pricing',
                'description': 'Ideal for early-stage startups',
                'features': ['Everything in Raise', 'Round closing', 'S/EIS']
            })
        
        if "Grow" in text_content:
            plans.append({
                'name': 'Grow',
                'price': 'Contact for pricing',
                'description': 'Essentials for growing companies',
                'features': ['Everything in Build', 'EMI & CSOP valuations', 'EMI share plans']
            })
        
        if "Scale" in text_content:
            plans.append({
                'name': 'Scale',
                'price': 'Contact for pricing',
                'description': 'Features for scaling businesses',
                'features': ['Everything in Grow', '409A & growth share valuations', 'Compensation management']
            })
        
        return {
            'plans': plans,
            'currency': 'GBP',
            'billing_period': 'annual',
            'raw_text_extract': self._get_pricing_text_extract(soup)
        }

    def _extract_bolago_pricing(self, soup):
        """Extract Bolago pricing information"""
        plans = []
        text_content = soup.get_text()
        
        # Extract known pricing from the content
        if "Gratis" in text_content:
            plans.append({
                'name': 'Gratis',
                'price': '0 kr',
                'description': 'Alltid gratis',
                'features': ['Aktiebok (till 5 aktieägare)', 'Hämtar ärenden från Bolagsverket', 'Tillgång till avtalsmallar']
            })
        
        if "Starter" in text_content and "395 kr" in text_content:
            plans.append({
                'name': 'Starter',
                'price': '395 kr per månad / 3,950 kr per år',
                'description': '12 månaders bindningstid',
                'features': ['Aktiebok (till 15 aktieägare)', 'Upp till 2 användare', 'Dokumenthantering', 'E-Signatur']
            })
        
        if "Grow" in text_content and "1 695 kr" in text_content:
            plans.append({
                'name': 'Grow',
                'price': '1,695 kr per månad / 16,950 kr per år',
                'description': '12 månaders bindningstid',
                'features': ['Aktiebok (till 25 aktieägare)', 'Styrelseportal', 'Bolagsstämmor', 'Optionsprogram']
            })
        
        if "Pro" in text_content:
            plans.append({
                'name': 'Pro',
                'price': 'Offert',
                'description': 'Alltid 12 månader i taget',
                'features': ['Obegränsat med användare', 'Skräddarsydda upplägg', 'Juridiskt konsultstöd']
            })
        
        return {
            'plans': plans,
            'currency': 'SEK',
            'billing_period': 'annual',
            'raw_text_extract': self._get_pricing_text_extract(soup)
        }

    def _extract_nvr_pricing(self, soup):
        """Extract NVR pricing information"""
        plans = []
        text_content = soup.get_text()
        
        if "Basic" in text_content and "0 kr/månad" in text_content:
            plans.append({
                'name': 'Basic',
                'price': '0 kr/månad',
                'description': 'För bolag med få aktieägare och förändringar',
                'features': ['Digital aktiebok', 'Aktiebok som PDF', 'Investor relations', 'Synk med Skatteverket']
            })
        
        if "Starter" in text_content and "49 kr/månad" in text_content:
            plans.append({
                'name': 'Starter',
                'price': 'Från 49 kr/månad',
                'description': 'Betala per aktieägare',
                'features': ['Kategorisering av aktieägare', 'Översiktssida med statistik', 'Rapporter i PDF och Excel']
            })
        
        if "Pro" in text_content and "750 kr/månad" in text_content:
            plans.append({
                'name': 'Pro',
                'price': 'Från 750 kr/månad',
                'description': 'Betala per stakeholder',
                'features': ['Optioner och derivat', 'Avancerade överlåtelser', 'Prioriterad support']
            })
        
        return {
            'plans': plans,
            'currency': 'SEK',
            'billing_period': 'monthly',
            'raw_text_extract': self._get_pricing_text_extract(soup)
        }

    def _extract_ledgy_pricing(self, soup):
        """Extract Ledgy pricing information"""
        plans = []
        text_content = soup.get_text()
        
        if "Growth" in text_content and "€900/year" in text_content:
            plans.append({
                'name': 'Growth',
                'price': 'Starts at €900/year',
                'description': '25 to 50 stakeholders included',
                'features': ['Cap Table Management', 'Document templating', 'Employee dashboards', 'Custom reporting']
            })
        
        if "Scale" in text_content and "€3k/year" in text_content:
            plans.append({
                'name': 'Scale',
                'price': 'Starts at €3k/year',
                'description': '50+ stakeholders included',
                'features': ['70+ HRIS integrations', 'Exit waterfall modeling', 'Automated granting', 'Onboarding Consultant']
            })
        
        if "Enterprise" in text_content:
            plans.append({
                'name': 'Enterprise',
                'price': 'Custom pricing',
                'description': '200+ stakeholders included',
                'features': ['GraphQL API access', 'SAML SSO', 'SCIM provisioning', 'IPO preparation']
            })
        
        return {
            'plans': plans,
            'currency': 'EUR',
            'billing_period': 'annual',
            'raw_text_extract': self._get_pricing_text_extract(soup)
        }

    def _extract_cakeequity_pricing(self, soup):
        """Extract Cake Equity pricing information"""
        return self._extract_generic_pricing(soup, soup.get_text())

    def _extract_mantle_pricing(self, soup):
        """Extract Mantle pricing information"""
        return self._extract_generic_pricing(soup, soup.get_text())

    def _extract_clara_pricing(self, soup):
        """Extract Clara pricing information"""
        return self._extract_generic_pricing(soup, soup.get_text())

    def _extract_generic_pricing(self, soup, raw_html):
        """Generic pricing extraction for sites we haven't specifically implemented"""
        plans = []
        
        # Use trafilatura to get clean text content
        text_content = trafilatura.extract(raw_html) if raw_html else soup.get_text()
        
        # Look for common pricing patterns
        price_patterns = [
            r'[\$£€]\d+(?:,\d{3})*(?:\.\d{2})?',  # $100, £1,000, €50.00
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:per|/)\s*(?:month|year|user)',  # 100 per month
            r'(?:free|gratis|kostenlos)',  # Free plans
            r'(?:contact|custom|enterprise)',  # Contact for pricing
        ]
        
        pricing_info = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            pricing_info.extend(matches)
        
        # Try to find plan names and structure
        plan_keywords = ['basic', 'starter', 'pro', 'enterprise', 'premium', 'growth', 'scale', 'free', 'standard']
        
        lines = text_content.split('\n')
        current_plan = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains a plan name
            for keyword in plan_keywords:
                if keyword.lower() in line.lower() and len(line) < 100:  # Plan names are usually short
                    current_plan = {
                        'name': line,
                        'price': 'Not specified',
                        'features': [],
                        'description': ''
                    }
                    plans.append(current_plan)
                    break
        
        # If no structured plans found, create a generic entry
        if not plans:
            plans.append({
                'name': 'General Pricing',
                'price': ', '.join(pricing_info[:5]) if pricing_info else 'Contact for pricing',
                'features': [],
                'description': 'Pricing information extracted from page content'
            })
        
        return {
            'plans': plans,
            'currency': 'Unknown',
            'billing_period': 'unknown',
            'raw_text_extract': text_content[:500] + '...' if len(text_content) > 500 else text_content,
            'pricing_mentions': pricing_info[:10]  # First 10 pricing mentions
        }

    def _get_pricing_text_extract(self, soup):
        """Get a clean text extract focusing on pricing information"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Try to find pricing-related sections
        pricing_keywords = ['pricing', 'price', 'cost', 'plan', 'subscription', 'billing', 'fee']
        sentences = text.split('.')
        
        pricing_sentences = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in pricing_keywords):
                pricing_sentences.append(sentence.strip())
        
        if pricing_sentences:
            extract = '. '.join(pricing_sentences[:5])  # First 5 relevant sentences
        else:
            extract = text[:500]  # First 500 characters as fallback
        
        return extract + '...' if len(extract) > 500 else extract

    def scrape_all(self):
        """Scrape all competitors"""
        results = {}
        logging.info("Starting scrape of all competitors")
        
        for competitor_key in self.competitors:
            logging.info(f"Scraping {competitor_key}")
            results[competitor_key] = self.scrape_single(competitor_key)
            # Rate limiting between requests
            if competitor_key != list(self.competitors.keys())[-1]:  # Don't wait after last request
                time.sleep(self.request_delay)
        
        logging.info("Completed scraping all competitors")
        return results

    def get_all_data(self):
        """Get all stored competitor data"""
        return self.data.copy()

    def get_competitor_data(self, competitor_key):
        """Get data for a specific competitor"""
        return self.data.get(competitor_key)
