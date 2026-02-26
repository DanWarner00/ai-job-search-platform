# Adzuna API Setup

Adzuna aggregates jobs from Indeed, Monster, CareerBuilder, and many other job boards. It's **free** and requires no approval process.

## Get API Credentials (Free)

1. **Sign up**: https://developer.adzuna.com/signup
2. **Create an account** (takes 2 minutes)
3. **Get your credentials**:
   - App ID
   - API Key

## Add to `.env` File

Open `C:\job_search_platform\.env` and add:

```
ADZUNA_APP_ID=your-app-id-here
ADZUNA_APP_KEY=your-api-key-here
```

## Test It

Run the scraper:
```powershell
flask scrape-jobs
```

Or click **"Find New Jobs"** in the UI.

## Coverage

Adzuna aggregates jobs from:
- Indeed
- Monster
- CareerBuilder
- Dice
- SimplyHired
- Government job sites
- Company career pages

## Limits

- **Free tier**: 5,000 API calls/month
- **Typical usage**: ~50 calls/day (100 jobs/day)
- **No approval needed**: Instant access

## Alternative APIs

If you want more sources, you can also add:

### JSearch (RapidAPI)
- Aggregates LinkedIn, Glassdoor, ZipRecruiter
- Free tier: 250 requests/month
- Signup: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

### The Muse
- Tech/startup focused jobs
- Free, unlimited
- No API key needed
- Docs: https://www.themuse.com/developers/api/v2
