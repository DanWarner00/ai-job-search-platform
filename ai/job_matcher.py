"""
AI-powered job matching using Claude API
"""
import anthropic
import os


def calculate_match_score(resume_text, job):
    """
    Calculate match score (0-100) between resume and job using Claude
    
    Args:
        resume_text: Full text from resume
        job: Job object with title, description, requirements, etc.
    
    Returns:
        tuple: (score: int, explanation: str) - Match score 0-100 and explanation
    """
    api_key = os.getenv('CLAUDE_API_KEY')
    
    if not api_key:
        # Return placeholder if no API key
        return (75, None)
    
    if not resume_text:
        return (50, None)
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build job details
        salary_str = f"${job.salary_min:,} - ${job.salary_max:,}" if job.salary_min and job.salary_max else 'Not specified'
        job_details = f"""
Job Title: {job.title}
Company: {job.company}
Location: {job.location or 'Not specified'}
Salary: {salary_str}
Description: {job.description[:1000] if job.description else 'Not provided'}
Requirements: {job.requirements[:500] if job.requirements else 'Not provided'}
"""
        
        prompt = f"""Analyze this job posting against the candidate's resume and provide a match score and explanation.

RESUME:
{resume_text[:3000]}

JOB POSTING:
{job_details}

Evaluate based on:
- Skills match (technical skills, tools, languages)
- Experience level fit
- Industry/domain alignment
- Location preferences
- Role responsibilities match

Respond in this EXACT format:
SCORE: [number 0-100]
EXPLANATION: [2-3 sentence explanation of why this score, highlighting key matches or gaps]

Example:
SCORE: 85
EXPLANATION: Strong match with 5+ years Python experience and ML background aligning with role requirements. Resume shows direct experience with required frameworks (TensorFlow, PyTorch). Minor gap in cloud infrastructure experience but transferable skills present."""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Cheaper/faster for scoring
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        response_text = message.content[0].text.strip()
        
        # Extract score and explanation
        score = 75  # Default
        explanation = None
        
        lines = response_text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('SCORE:'):
                score_text = line.replace('SCORE:', '').strip()
                score = int(score_text)
            elif line.startswith('EXPLANATION:'):
                # Get explanation (might be multi-line)
                explanation = line.replace('EXPLANATION:', '').strip()
                # Add any following lines
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        explanation += ' ' + lines[j].strip()
        
        # Ensure score is in range
        score = max(0, min(100, score))
        
        return (score, explanation)
        
    except Exception as e:
        print(f"Error calculating match score: {e}")
        return (75, None)  # Default fallback


def batch_score_jobs(resume_text, jobs, limit=10):
    """
    Score multiple jobs efficiently
    Only scores top N jobs to save API calls
    """
    scored_jobs = []
    
    for job in jobs[:limit]:
        score = calculate_match_score(resume_text, job)
        scored_jobs.append((job, score))
    
    return scored_jobs
