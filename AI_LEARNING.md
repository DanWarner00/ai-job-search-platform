# AI Learning from "Not Interested" Feedback

## Overview
Users can drag jobs to the "Not Interested" column in the Kanban board. This feedback will be used to train the AI to better understand the user's preferences and filter out irrelevant jobs in future scrapes.

## Current Status
✅ UI implemented - "Not Interested" column in Kanban board
✅ Database tracking - `status='not_interested'` in applications table
⏳ AI learning logic - Coming soon

## Future Implementation

### Phase 1: Pattern Analysis
When a user marks jobs as "not interested", analyze:
- **Job titles** - certain keywords they avoid (e.g., "Senior" if they're junior level)
- **Companies** - specific companies or company sizes they're not interested in
- **Locations** - remote vs onsite, specific cities/states
- **Salary ranges** - jobs outside their target range
- **Requirements** - skills/experience they don't have or want to avoid (e.g., "5+ years Java" when they're Python-focused)
- **Job descriptions** - keywords in descriptions that signal disinterest

### Phase 2: Automatic Filtering
Use Claude API to:
1. Analyze all jobs in the `not_interested` status
2. Extract common patterns (use prompt like: "Analyze these job postings and tell me what requirements or characteristics they have in common")
3. When scraping new jobs, automatically score them lower if they match "not interested" patterns
4. Option to auto-hide jobs with match scores below threshold

### Phase 3: Smart Recommendations
- Provide explanations: "This job was ranked lower because similar jobs were marked 'Not Interested'"
- Allow user to override: "Show me these anyway" button
- Weekly summary: "You seem to avoid jobs with [X], should I keep filtering these?"

## Database Schema
Already implemented:
```python
# Applications table already supports not_interested status
status = db.Column(db.String(50))  # Values: not_applied, applied, interview, rejected, offer, not_interested
```

## API Endpoints Needed
- `POST /api/ai/analyze-preferences` - Analyze not_interested jobs and update user preferences
- `GET /api/ai/learning-insights` - Show what the AI has learned about user preferences

## Claude API Integration
Use the `anthropic` library (already in requirements.txt):
```python
import anthropic

def analyze_not_interested_jobs(user_id):
    # Get all not_interested jobs
    not_interested = Application.query.filter_by(
        status='not_interested'
    ).join(Job).all()
    
    # Build prompt with job details
    jobs_text = "\n\n".join([
        f"Title: {app.job.title}\nCompany: {app.job.company}\n"
        f"Location: {app.job.location}\nSalary: {app.job.salary_min}-{app.job.salary_max}\n"
        f"Description: {app.job.description[:500]}"
        for app in not_interested
    ])
    
    # Ask Claude to analyze patterns
    client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Analyze these job postings that a user marked as 'Not Interested'. "
                      f"Extract common patterns in requirements, titles, companies, locations, or "
                      f"job characteristics that the user is avoiding:\n\n{jobs_text}"
        }]
    )
    
    return message.content[0].text
```

## Notes
- Start collecting data now (users marking jobs as not_interested)
- Implement AI analysis after collecting 10+ not_interested jobs
- Make sure AI learning is transparent - show users what it learned
- Allow users to disable AI filtering if they want full control
