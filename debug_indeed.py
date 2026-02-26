"""Debug Indeed page structure"""
from playwright.sync_api import sync_playwright
import time

print('🔍 Debugging Indeed page structure...\n')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show browser
    page = browser.new_page()
    
    url = "https://www.indeed.com/jobs?q=Data+Analyst&l=Portland,+OR"
    print(f'Navigating to: {url}')
    
    page.goto(url, wait_until='networkidle', timeout=30000)
    
    # Take screenshot
    page.screenshot(path='indeed_screenshot.png')
    print('✅ Screenshot saved: indeed_screenshot.png')
    
    # Save HTML
    html = page.content()
    with open('indeed_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('✅ HTML saved: indeed_page.html')
    
    # Try to find job cards with different selectors
    print('\n🔍 Testing selectors:')
    
    selectors_to_try = [
        'div.job_seen_beacon',
        'div.slider_item',
        'div[data-jk]',
        'div.jobsearch-SerpJobCard',
        'div[id^="job_"]',
        'a.jcs-JobTitle',
        'h2.jobTitle',
        'div.cardOutline',
        'li.css-5lfssm',
        'div[class*="job"]',
    ]
    
    for selector in selectors_to_try:
        try:
            elements = page.query_selector_all(selector)
            print(f'   {selector}: {len(elements)} found')
            if len(elements) > 0 and len(elements) < 100:  # Reasonable number
                print(f'      ✅ This might be it!')
        except Exception as e:
            print(f'   {selector}: Error - {e}')
    
    # Get all divs with class containing "job"
    print('\n🔍 Looking for divs with "job" in class name...')
    all_divs = page.query_selector_all('div[class*="job" i], div[class*="card" i]')
    
    # Get unique class names
    class_names = set()
    for div in all_divs[:50]:  # Check first 50
        classes = div.get_attribute('class')
        if classes:
            class_names.update(classes.split())
    
    job_related = [c for c in class_names if 'job' in c.lower() or 'card' in c.lower()]
    print(f'Found {len(job_related)} unique job/card-related classes:')
    for c in sorted(job_related)[:20]:
        print(f'   - {c}')
    
    print('\n⏸️  Pausing for 5 seconds so you can see the browser...')
    time.sleep(5)
    
    browser.close()
    
print('\n✅ Debug complete! Check indeed_screenshot.png and indeed_page.html')
