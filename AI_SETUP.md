# AI Features Setup

## Features Added
1. **Real Match Scores** - AI calculates 0-100% match based on your resume
2. **AI Cover Letters** - Generate personalized cover letters for any job
3. **Advanced Filters** - Filter by match score range, date posted, date scraped

## Setup Instructions

### 1. Add Claude API Key

Edit `C:\job_search_platform\.env` and add:
```
CLAUDE_API_KEY=your_claude_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 2. Calculate Match Scores

After uploading your resume and scraping jobs, run:
```bash
cd C:\job_search_platform
flask calculate-matches
```

This will:
- Parse your resume
- Calculate AI match scores for all jobs
- Update the database (may take a few minutes for many jobs)

**Note:** Match scoring uses Claude API and costs ~$0.01-0.02 per job.

### 3. Use Cover Letter Generator

On any job detail page:
1. Click "Generate Cover Letter"
2. AI will create a personalized cover letter
3. Copy and customize as needed

## Usage

### Match Scores
- Jobs now show real 0-100% match scores
- Green (80-100%): Excellent match
- Yellow (60-79%): Good match  
- Red (<60%): Poor match

### Filters
Click "Show Filters" on Jobs page:
- **Match Score Range**: Filter by min/max % match
- **Sort By**: Match Score, Date Posted, or Date Scraped
- **Location**: Filter by city/state
- **Source**: Filter by job board

### Cover Letters
- Click "Generate Cover Letter" on job detail pages
- Uses your resume + job description
- Takes ~10 seconds to generate
- Can copy to clipboard

## Cost Estimate

- Match scoring: ~$0.01 per job (one-time per job)
- Cover letter: ~$0.03 per letter
- Example: 50 jobs scored + 10 cover letters = ~$0.80

## Troubleshooting

**"Error: Claude API key not configured"**
→ Add CLAUDE_API_KEY to .env file

**"No resume uploaded"**
→ Go to Settings and upload your resume (PDF)

**Match scores still showing 75%**
→ Run `flask calculate-matches` after uploading resume

**Cover letter generation fails**
→ Check that Claude API key is valid and has credits
