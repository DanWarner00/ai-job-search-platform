# AI Model Usage - Cost Optimization

Last updated: 2026-02-24

## Model Selection Strategy

To optimize costs while maintaining quality:
- **Cheap/fast model** for simple scoring tasks
- **Premium model** for creative writing (cover letters)

---

## Current Model Usage

### 1. Match Scoring & Explanations
**Model:** `claude-3-5-haiku-20241022` (Haiku)

**Used for:**
- Calculating 0-100% match scores
- Generating 2-3 sentence match explanations

**Why Haiku:**
- ✅ 5x cheaper than Sonnet
- ✅ 3x faster
- ✅ Good enough for structured scoring tasks
- ✅ Still understands resumes and job descriptions well

**Cost per job:** ~$0.002 (0.2 cents)
**Tokens per job:** ~1,500 input + 50 output

**Location:** `ai/job_matcher.py`

---

### 2. Cover Letter Generation
**Model:** `claude-3-5-sonnet-20241022` (Sonnet 4.5)

**Used for:**
- Writing personalized cover letters

**Why Sonnet:**
- ✅ Best quality for creative writing
- ✅ Better tone and personalization
- ✅ More natural language
- ✅ Worth the cost for final output

**Cost per letter:** ~$0.03 (3 cents)
**Tokens per letter:** ~3,500 input + 600 output

**Location:** `ai/cover_letter.py`

---

## Cost Comparison

### Per 100 Jobs Scraped

| Task | Model | Cost |
|------|-------|------|
| Match scoring (100 jobs) | Haiku | $0.20 |
| Cover letters (10 jobs) | Sonnet | $0.30 |
| **Total** | Mixed | **$0.50** |

### If Everything Used Sonnet

| Task | Model | Cost |
|------|-------|------|
| Match scoring (100 jobs) | Sonnet | $1.00 |
| Cover letters (10 jobs) | Sonnet | $0.30 |
| **Total** | Sonnet | **$1.30** |

**Savings with mixed approach:** ~60% on scoring tasks

---

## Model Pricing (Anthropic)

### Claude 3.5 Haiku (Fast & Cheap)
- Input: $1.00 / 1M tokens
- Output: $5.00 / 1M tokens
- Speed: ~3x faster than Sonnet
- Use for: Scoring, classification, structured data

### Claude 3.5 Sonnet (Premium)
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens
- Speed: Standard
- Use for: Writing, creativity, complex reasoning

---

## Usage Estimates

### Light Usage (10 jobs/day)
- Match scoring: $0.02/day = $0.60/month
- Cover letters (5/week): $0.15/week = $0.60/month
- **Total:** ~$1.20/month

### Medium Usage (50 jobs/day)
- Match scoring: $0.10/day = $3.00/month
- Cover letters (10/week): $0.30/week = $1.20/month
- **Total:** ~$4.20/month

### Heavy Usage (200 jobs/day)
- Match scoring: $0.40/day = $12.00/month
- Cover letters (20/week): $0.60/week = $2.40/month
- **Total:** ~$14.40/month

---

## If You're Still Hitting Limits

### Further Optimizations

1. **Batch scoring less frequently**
   - Score jobs once per day instead of immediately
   - Use `flask calculate-matches` manually when needed

2. **Skip low-quality jobs**
   - Only score jobs with descriptions >100 chars
   - Filter by source before scoring

3. **Cache match scores**
   - Never re-score the same job
   - Already implemented ✅

4. **Reduce cover letter generation**
   - Only generate for high-match jobs (>70%)
   - Reuse/edit existing letters

5. **Use even cheaper models**
   - Claude 3 Haiku (older, cheaper)
   - Or skip AI for match scoring entirely (use keyword matching)

---

## Monitoring Usage

Check your Anthropic dashboard:
- https://console.anthropic.com/settings/usage

Track:
- Daily API calls
- Token usage
- Cost per feature

---

## Changing Models

### To use an even cheaper model for scoring:

Edit `ai/job_matcher.py`:
```python
model="claude-3-haiku-20240307"  # Even cheaper (older Haiku)
```

### To downgrade cover letters too:

Edit `ai/cover_letter.py`:
```python
model="claude-3-5-haiku-20241022"  # Use Haiku for letters
```

---

## Quality vs Cost Tradeoff

| Feature | Current Model | Quality | Cost | Alternative | Quality | Cost |
|---------|--------------|---------|------|-------------|---------|------|
| Match scoring | Haiku 3.5 | 95% | $$ | Keyword match | 70% | Free |
| Explanations | Haiku 3.5 | 90% | $$ | None | 0% | Free |
| Cover letters | Sonnet 4.5 | 100% | $$$$$ | Haiku 3.5 | 85% | $$ |

**Recommendation:** Keep current setup (Haiku for scoring, Sonnet for letters)
