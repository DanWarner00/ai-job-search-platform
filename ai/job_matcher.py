"""
AI-powered job matching using Claude API
"""
import anthropic
import os


def calculate_match_score(resume_text, job, prefs=None):
    """
    Calculate match score (0-100) between resume and job using Claude

    Args:
        resume_text: Full text from resume
        job: Job object with title, description, requirements, etc.
        prefs: Optional SearchPreferences object for keyword/goal context

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
        
        prefs_context = ""
        if prefs:
            if prefs.keywords and prefs.keywords.strip():
                prefs_context += f"\nCandidate's Priority Keywords: {prefs.keywords.strip()}"
            if prefs.search_description and prefs.search_description.strip():
                prefs_context += f"\nCandidate's Search Goals: {prefs.search_description.strip()}"

        prompt = f"""Analyze this job posting against the candidate's resume and provide a match score and explanation.

RESUME:
{resume_text[:3000]}
{prefs_context}

JOB POSTING:
{job_details}

Evaluate based on:
- Skills match (technical skills, tools, languages)
- Experience level fit
- Industry/domain alignment — weight higher if job aligns with candidate's priority keywords
- Location preferences
- Role responsibilities match

Respond in this EXACT format:
SCORE: [number 0-100]
EXPLANATION: [2-3 sentence explanation of why this score, highlighting key matches or gaps]

Example:
SCORE: 85
EXPLANATION: Strong match with 5+ years Python experience and ML background aligning with role requirements. Resume shows direct experience with required frameworks (TensorFlow, PyTorch). Minor gap in cloud infrastructure experience but transferable skills present."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
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


def generate_match_analysis(resume_text, job, prefs=None):
    """
    Generate a detailed, personalized match analysis for a specific job.
    Called on-demand by the user rather than automatically during scraping.

    Args:
        resume_text: Full text from resume
        job: Job object
        prefs: Optional SearchPreferences object

    Returns:
        str: Detailed analysis paragraph
    """
    api_key = os.getenv('CLAUDE_API_KEY')

    if not api_key:
        return "Claude API key not configured."

    if not resume_text:
        return "No resume found. Please upload your resume first."

    try:
        client = anthropic.Anthropic(api_key=api_key)

        salary_str = f"${job.salary_min:,} - ${job.salary_max:,}" if job.salary_min and job.salary_max else 'Not specified'
        job_details = f"""Job Title: {job.title}
Company: {job.company}
Location: {job.location or 'Not specified'}
Salary: {salary_str}
Description: {job.description[:2000] if job.description else 'Not provided'}
Requirements: {job.requirements[:1000] if job.requirements else 'Not provided'}"""

        search_context = ""
        if prefs:
            if prefs.search_description:
                search_context += f"\nCandidate's Job Search Goals: {prefs.search_description}"
            if prefs.work_experience:
                search_context += f"\nAdditional Work Experience Context: {prefs.work_experience}"

        prompt = f"""You are helping a job seeker understand how well a specific job matches their profile. Be honest, specific, and personal — reference actual details from their resume and the job posting.

CANDIDATE RESUME:
{resume_text[:3000]}
{search_context}

JOB POSTING:
{job_details}

Write 3-4 sentences covering:
- Specific skills or experience from the resume that align with this role
- Any meaningful gaps or concerns
- Whether this role fits their apparent career direction
- A candid overall take

Be direct and concrete. Reference actual resume details and job requirements — not generic advice."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text.strip()

    except Exception as e:
        print(f"Error generating match analysis: {e}")
        return f"Could not generate analysis: {str(e)}"
