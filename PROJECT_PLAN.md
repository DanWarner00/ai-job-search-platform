# Job Search Platform - Project Plan

## Vision
AI-powered job search assistant that scrapes multiple job boards, matches opportunities to your resume, tracks applications, and helps you land your next role.

**Tech Stack:** Python (Flask), SQLite, Claude AI, Tailwind CSS

---

## Phase 1: MVP (Week 1-2)
**Goal:** Basic scraping + tracking working

### Features:
- [ ] Scrape Indeed, LinkedIn (basic)
- [ ] Simple job listing page
- [ ] Manual status tracking (Applied, Interview, Rejected, Not Interested)
- [ ] Basic filtering (title, location, posted date)
- [ ] SQLite database

### Files to Create:
```
job_search_platform/
├── app.py                 # Flask app
├── scrapers/
│   ├── indeed.py
│   ├── linkedin.py
│   └── base.py
├── models.py              # Database models
├── templates/
│   ├── index.html
│   ├── job_detail.html
│   └── dashboard.html
├── static/
│   ├── style.css
│   └── app.js
├── requirements.txt
└── README.md
```

---

## Phase 2: AI Integration (Week 3)
**Goal:** Resume matching + smart features

### Features:
- [ ] Upload resume (PDF/DOCX)
- [ ] AI match scoring (0-100)
- [ ] Auto-generate cover letters
- [ ] Resume tailoring suggestions
- [ ] Interview question generator

### New Files:
```
├── ai/
│   ├── resume_parser.py
│   ├── job_matcher.py
│   └── cover_letter.py
├── uploads/              # Store user resumes
└── prompts/             # Claude prompts
```

---

## Phase 3: Automation (Week 4)
**Goal:** Scheduled scraping + notifications

### Features:
- [ ] Daily auto-scrape (Celery cron)
- [ ] Email/Telegram notifications for new matches
- [ ] Gmail integration (detect interview invites)
- [ ] Follow-up reminders

### New Files:
```
├── tasks.py              # Celery background tasks
├── notifications/
│   ├── email.py
│   └── telegram.py
└── integrations/
    └── gmail.py
```

---

## Phase 4: Analytics (Week 5)
**Goal:** Dashboard with insights

### Features:
- [ ] Application funnel visualization
- [ ] Weekly goal tracking (chart)
- [ ] Company response time analytics
- [ ] Salary heatmap
- [ ] Success pattern detection

### New Files:
```
├── analytics/
│   ├── dashboard.py
│   └── insights.py
└── templates/
    └── analytics.html
```

---

## Phase 5: Polish (Week 6)
**Goal:** Production-ready

### Features:
- [ ] User authentication (multi-user support)
- [ ] Export data (CSV, PDF reports)
- [ ] Dark mode
- [ ] Mobile responsive
- [ ] Deployment (Railway/Render/Fly.io)

---

## OpenClaw Integration Ideas

1. **Voice Commands**
   - "Find me senior Python jobs in Portland"
   - "Show me jobs I applied to this week"
   - "Generate a cover letter for this job"

2. **Daily Briefing**
   - Auto-run every morning at 8 AM
   - Send Telegram message: "5 new high-match jobs today"

3. **Smart Assistant**
   - "Should I apply to this job?" → AI analyzes fit
   - "Prepare me for an interview at Company X" → Research + questions

4. **Automated Follow-ups**
   - Detect no response after 2 weeks → Draft follow-up email

---

## What to Build First?

**Recommend starting with:**
1. Basic Flask app + database
2. Indeed scraper (easiest to start with)
3. Simple job listing page
4. Status tracking UI

Then iterate from there.

---

## Questions to Answer:

1. **Resume format?** PDF, DOCX, or paste text?
2. **Scraping frequency?** Daily? Real-time?
3. **User accounts?** Just you, or multi-user?
4. **Mobile app?** Or web-only?
5. **Integration priority?** Which job boards matter most?

---

## Next Steps:

1. Set up Flask boilerplate
2. Build Indeed scraper
3. Create database schema
4. Build basic UI

Let me know what you want to tackle first!
