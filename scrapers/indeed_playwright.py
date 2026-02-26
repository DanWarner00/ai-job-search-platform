"""
Indeed scraper using Playwright (headless browser)
More reliable than requests - harder for Indeed to block
"""
from playwright.sync_api import sync_playwright
import hashlib
from datetime import datetime
import re


class IndeedPlaywrightScraper:
    """Scraper for Indeed using Playwright"""
    
    def __init__(self):
        self.base_url = "https://www.indeed.com"
        self.jobs = []
    
    def scrape(self, keywords='python developer', location='Portland, OR', max_results=50):
        """Scrape jobs from Indeed using real browser"""
        print(f'🔍 Scraping Indeed for: {keywords} in {location}')
        
        with sync_playwright() as p:
            # Launch browser (headless=False to avoid detection)
            browser = p.chromium.launch(
                headless=False,  # Show browser to avoid detection
                args=['--disable-blink-features=AutomationControlled']  # Hide automation
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Build search URL
            search_url = f"{self.base_url}/jobs?q={keywords}&l={location}"
            
            try:
                # Navigate to Indeed
                print(f'   Navigating to: {search_url}')
                page.goto(search_url, timeout=30000)
                
                # Wait for page to fully load
                import time
                print(f'   Waiting for page to load...')
                time.sleep(5)  # Give Indeed time to render
                
                # Get all job cards (try multiple selectors, don't wait)
                job_cards = page.query_selector_all('.job_seen_beacon')
                
                if not job_cards:
                    print(f'   No .job_seen_beacon found, trying .cardOutline...')
                    job_cards = page.query_selector_all('.cardOutline')
                
                if not job_cards:
                    print(f'   No .cardOutline found, trying .slider_item...')
                    job_cards = page.query_selector_all('.slider_item')
                
                print(f'   Found {len(job_cards)} job cards')
                
                for i, card in enumerate(job_cards[:max_results]):
                    try:
                        job_data = self.parse_job_card_playwright(card, page)
                        if job_data:
                            self.jobs.append(job_data)
                            print(f'   ✅ Parsed: {job_data["title"][:50]}...')
                    except Exception as e:
                        print(f'   ⚠️  Error parsing job {i}: {e}')
                        continue
                
            except Exception as e:
                print(f'   ❌ Error during scraping: {e}')
            finally:
                browser.close()
        
        print(f'✅ Successfully scraped {len(self.jobs)} jobs from Indeed')
        return self.jobs
    
    def parse_job_card_playwright(self, card, page):
        """Parse a single job card using Playwright selectors"""
        # Extract title
        title_elem = card.query_selector('h2.jobTitle, .jobTitle span')
        if not title_elem:
            return None
        title = title_elem.inner_text().strip()
        
        # Extract company
        company_elem = card.query_selector('[data-testid="company-name"], .companyName')
        company = company_elem.inner_text().strip() if company_elem else 'Unknown'
        
        # Extract location
        location_elem = card.query_selector('[data-testid="text-location"], .companyLocation')
        location = location_elem.inner_text().strip() if location_elem else None
        
        # Extract job URL
        link_elem = card.query_selector('h2.jobTitle a, a.jcs-JobTitle')
        if not link_elem:
            return None
        
        job_url = link_elem.get_attribute('href')
        if not job_url.startswith('http'):
            job_url = self.base_url + job_url
        
        # Extract job ID from URL
        job_id_match = re.search(r'jk=([a-f0-9]+)', job_url)
        job_id = job_id_match.group(1) if job_id_match else hashlib.md5(job_url.encode()).hexdigest()
        
        # Extract salary
        salary_elem = card.query_selector('.salary-snippet-container, .metadata.salary-snippet-container')
        salary_min, salary_max = None, None
        if salary_elem:
            salary_text = salary_elem.inner_text().strip()
            salary_min, salary_max = self.clean_salary(salary_text)
        
        # Extract description snippet
        snippet_elem = card.query_selector('.job-snippet, [data-testid="job-snippet"]')
        description = snippet_elem.inner_text().strip() if snippet_elem else ''
        
        return {
            'source': 'indeed',
            'external_id': job_id,
            'url': job_url,
            'title': title,
            'company': company,
            'location': location,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'description': description,
            'requirements': None,
            'posted_date': None  # Indeed doesn't always show this on cards
        }
    
    def clean_salary(self, salary_text):
        """Extract min/max salary from text"""
        if not salary_text:
            return None, None
        
        # Remove common words
        salary_text = salary_text.lower().replace('a year', '').replace('an hour', '')
        salary_text = salary_text.replace(',', '').replace('$', '')
        
        # Try to find numbers
        numbers = re.findall(r'(\d+(?:\.\d+)?)[k]?', salary_text)
        
        if len(numbers) >= 2:
            # Range found
            min_sal = float(numbers[0])
            max_sal = float(numbers[1])
            
            # Handle 'k' notation
            if 'k' in salary_text:
                min_sal *= 1000
                max_sal *= 1000
            
            return int(min_sal), int(max_sal)
        elif len(numbers) == 1:
            # Single number
            salary = float(numbers[0])
            if 'k' in salary_text:
                salary *= 1000
            return int(salary), int(salary)
        
        return None, None


# Test
if __name__ == '__main__':
    scraper = IndeedPlaywrightScraper()
    jobs = scraper.scrape('Python Developer', 'Portland, OR', max_results=5)
    
    print(f'\n📊 Results:')
    for i, job in enumerate(jobs, 1):
        print(f'\n{i}. {job["title"]}')
        print(f'   Company: {job["company"]}')
        print(f'   Location: {job["location"]}')
        print(f'   URL: {job["url"][:80]}...')
