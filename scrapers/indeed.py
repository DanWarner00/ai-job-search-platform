"""
Indeed job scraper - Using Playwright for browser automation
"""
import requests
from bs4 import BeautifulSoup
import hashlib
import time
from .base import BaseScraper


class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.indeed.com"
        # Enhanced headers to look like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def scrape(self, keywords='python developer', location='Portland, OR', max_results=50):
        """
        Scrape jobs from Indeed
        
        Args:
            keywords: Job search keywords
            location: Job location
            max_results: Maximum number of jobs to scrape
            
        Returns:
            List of job dictionaries
        """
        print(f'Scraping Indeed for: {keywords} in {location}')
        
        search_url = f"{self.base_url}/jobs"
        params = {
            'q': keywords,
            'l': location,
            'limit': 50
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f'Error fetching Indeed jobs: {e}')
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job cards
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        if not job_cards:
            # Try alternative selector
            job_cards = soup.find_all('a', class_='jcs-JobTitle')
        
        print(f'Found {len(job_cards)} job cards')
        
        for card in job_cards[:max_results]:
            try:
                job_data = self.parse_job_card(card)
                if job_data:
                    self.jobs.append(job_data)
            except Exception as e:
                print(f'Error parsing job card: {e}')
                continue
        
        print(f'Successfully parsed {len(self.jobs)} jobs')
        return self.jobs
    
    def parse_job_card(self, card):
        """
        Parse a single Indeed job card
        
        Args:
            card: BeautifulSoup element of job card
            
        Returns:
            Dictionary with job data
        """
        # Try to extract title
        title_elem = card.find('h2', class_='jobTitle') or card.find('a', class_='jcs-JobTitle')
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        
        # Extract job URL and ID
        link_elem = card.find('a', class_='jcs-JobTitle') or title_elem.find('a')
        if not link_elem or not link_elem.get('href'):
            return None
        
        job_url = link_elem['href']
        if not job_url.startswith('http'):
            job_url = self.base_url + job_url
        
        # Generate external ID from URL (Indeed job key)
        job_id = job_url.split('jk=')[-1].split('&')[0] if 'jk=' in job_url else hashlib.md5(job_url.encode()).hexdigest()
        
        # Extract company
        company_elem = card.find('span', class_='companyName')
        company = company_elem.get_text(strip=True) if company_elem else 'Unknown'
        
        # Extract location
        location_elem = card.find('div', class_='companyLocation')
        location = location_elem.get_text(strip=True) if location_elem else None
        
        # Extract salary (if available)
        salary_elem = card.find('div', class_='salary-snippet')
        salary_min, salary_max = None, None
        if salary_elem:
            salary_text = salary_elem.get_text(strip=True)
            salary_min, salary_max = self.clean_salary(salary_text)
        
        # Extract posted date
        date_elem = card.find('span', class_='date')
        posted_date = None
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            posted_date = self.parse_date(date_text)
        
        # Extract job snippet/description
        snippet_elem = card.find('div', class_='job-snippet')
        description = snippet_elem.get_text(strip=True) if snippet_elem else ''
        
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
            'requirements': None,  # Full requirements need detailed page scrape
            'posted_date': posted_date
        }


# Test scraper
if __name__ == '__main__':
    scraper = IndeedScraper()
    jobs = scraper.scrape('python developer', 'Portland, OR', max_results=10)
    
    print(f'\nScraped {len(jobs)} jobs:')
    for job in jobs[:3]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
