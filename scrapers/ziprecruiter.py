"""
ZipRecruiter job scraper
"""
import requests
from bs4 import BeautifulSoup
import hashlib
from .base import BaseScraper


class ZipRecruiterScraper(BaseScraper):
    """Scraper for ZipRecruiter"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ziprecruiter.com"
    
    def scrape(self, keywords='python developer', location='Portland, OR', max_results=50):
        """
        Scrape jobs from ZipRecruiter
        """
        print(f'Scraping ZipRecruiter for: {keywords} in {location}')
        
        search_url = f"{self.base_url}/jobs-search"
        params = {
            'search': keywords,
            'location': location,
            'days': 7  # Last 7 days
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f'Error fetching ZipRecruiter jobs: {e}')
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job cards
        job_cards = soup.find_all('article', class_='job_result')
        
        if not job_cards:
            # Try alternative selectors
            job_cards = soup.find_all('div', {'data-job-id': True})
        
        print(f'Found {len(job_cards)} job cards')
        
        for card in job_cards[:max_results]:
            try:
                job_data = self.parse_job_card(card)
                if job_data:
                    self.jobs.append(job_data)
            except Exception as e:
                print(f'Error parsing ZipRecruiter job card: {e}')
                continue
        
        print(f'Successfully parsed {len(self.jobs)} jobs')
        return self.jobs
    
    def parse_job_card(self, card):
        """
        Parse a single ZipRecruiter job card
        """
        # Extract job ID
        job_id = card.get('data-job-id') or card.get('id', '')
        if not job_id:
            # Generate from content
            job_id = hashlib.md5(str(card)[:100].encode()).hexdigest()[:16]
        
        # Extract title and URL
        title_elem = card.find('h2', class_='title') or card.find('a', {'data-job-title': True})
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        
        # Extract link
        link_elem = title_elem.find('a') if title_elem.name != 'a' else title_elem
        if not link_elem or not link_elem.get('href'):
            return None
        
        job_url = link_elem['href']
        if not job_url.startswith('http'):
            job_url = self.base_url + job_url
        
        # Extract company
        company_elem = card.find('a', class_='company_name') or card.find('span', class_='company')
        company = company_elem.get_text(strip=True) if company_elem else 'Unknown'
        
        # Extract location
        location_elem = card.find('span', class_='location') or card.find('div', class_='location')
        location = location_elem.get_text(strip=True) if location_elem else None
        
        # Extract salary (if available)
        salary_elem = card.find('span', class_='salary') or card.find('div', class_='payout')
        salary_min, salary_max = None, None
        if salary_elem:
            salary_text = salary_elem.get_text(strip=True)
            salary_min, salary_max = self.clean_salary(salary_text)
        
        # Extract posted date
        date_elem = card.find('time') or card.find('span', class_='days')
        posted_date = None
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            posted_date = self.parse_date(date_text)
        
        # Extract job snippet
        snippet_elem = card.find('p', class_='job_snippet') or card.find('div', class_='summary')
        description = snippet_elem.get_text(strip=True) if snippet_elem else ''
        
        return {
            'source': 'ziprecruiter',
            'external_id': job_id,
            'url': job_url,
            'title': title,
            'company': company,
            'location': location,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'description': description,
            'requirements': None,
            'posted_date': posted_date
        }


if __name__ == '__main__':
    scraper = ZipRecruiterScraper()
    jobs = scraper.scrape('python developer', 'Portland, OR', max_results=10)
    
    print(f'\nScraped {len(jobs)} jobs:')
    for job in jobs[:3]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
