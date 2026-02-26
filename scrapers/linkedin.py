"""
LinkedIn job scraper
Note: LinkedIn heavily rate-limits and requires authentication for full access.
This is a basic scraper that works without auth but has limitations.
"""
import requests
from bs4 import BeautifulSoup
import hashlib
from .base import BaseScraper


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn Jobs"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.linkedin.com"
        # LinkedIn requires more realistic headers
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
    
    def scrape(self, keywords='python developer', location='Portland, OR', max_results=50):
        """
        Scrape jobs from LinkedIn
        
        Note: LinkedIn's public job search is limited without authentication.
        Consider using their API with proper credentials for production use.
        """
        print(f'Scraping LinkedIn for: {keywords} in {location}')
        
        search_url = f"{self.base_url}/jobs/search"
        params = {
            'keywords': keywords,
            'location': location,
            'f_TPR': 'r604800',  # Past week
            'position': 1,
            'pageNum': 0
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f'Error fetching LinkedIn jobs: {e}')
            print('Note: LinkedIn may require authentication for reliable scraping')
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # LinkedIn job cards
        job_cards = soup.find_all('div', class_='base-card')
        
        if not job_cards:
            # Try alternative selector
            job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
        
        print(f'Found {len(job_cards)} job cards')
        
        for card in job_cards[:max_results]:
            try:
                job_data = self.parse_job_card(card)
                if job_data:
                    self.jobs.append(job_data)
            except Exception as e:
                print(f'Error parsing LinkedIn job card: {e}')
                continue
        
        print(f'Successfully parsed {len(self.jobs)} jobs')
        return self.jobs
    
    def parse_job_card(self, card):
        """
        Parse a single LinkedIn job card
        """
        # Extract title and link
        title_elem = card.find('h3', class_='base-search-card__title') or card.find('a', class_='base-card__full-link')
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        
        # Extract job URL
        link_elem = card.find('a', class_='base-card__full-link')
        if not link_elem or not link_elem.get('href'):
            return None
        
        job_url = link_elem['href']
        if not job_url.startswith('http'):
            job_url = self.base_url + job_url
        
        # Extract job ID from URL
        job_id = job_url.split('/')[-1].split('?')[0] if '/' in job_url else hashlib.md5(job_url.encode()).hexdigest()
        
        # Extract company
        company_elem = card.find('h4', class_='base-search-card__subtitle') or card.find('a', class_='hidden-nested-link')
        company = company_elem.get_text(strip=True) if company_elem else 'Unknown'
        
        # Extract location
        location_elem = card.find('span', class_='job-search-card__location')
        location = location_elem.get_text(strip=True) if location_elem else None
        
        # Extract posted date
        date_elem = card.find('time', class_='job-search-card__listdate')
        posted_date = None
        if date_elem:
            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
            posted_date = self.parse_date(date_text)
        
        return {
            'source': 'linkedin',
            'external_id': job_id,
            'url': job_url,
            'title': title,
            'company': company,
            'location': location,
            'salary_min': None,  # LinkedIn rarely shows salary in search results
            'salary_max': None,
            'description': '',  # Requires detail page scrape
            'requirements': None,
            'posted_date': posted_date
        }


if __name__ == '__main__':
    scraper = LinkedInScraper()
    jobs = scraper.scrape('python developer', 'Portland, OR', max_results=10)
    
    print(f'\nScraped {len(jobs)} jobs:')
    for job in jobs[:3]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"URL: {job['url']}")
