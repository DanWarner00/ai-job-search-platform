"""
AI-powered cover letter generation using Claude API
"""
import anthropic
import os


def generate_cover_letter(resume_text, job, user_preferences=None):
    """
    Generate a personalized cover letter using Claude
    
    Args:
        resume_text: Full text from resume
        job: Job object with title, description, company, etc.
        user_preferences: Optional dict with user's job search preferences
    
    Returns:
        str: Generated cover letter
    """
    api_key = os.getenv('CLAUDE_API_KEY')
    
    if not api_key:
        return "Error: Claude API key not configured. Add CLAUDE_API_KEY to .env file."
    
    if not resume_text:
        return "Error: Resume not found. Please upload your resume first."
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build job details
        job_details = f"""
Job Title: {job.title}
Company: {job.company}
Location: {job.location or 'Not specified'}
Description: {job.description[:2000] if job.description else 'Not provided'}
Requirements: {job.requirements[:1000] if job.requirements else 'Not provided'}
"""
        
        # Add user preferences context if available
        preferences_context = ""
        if user_preferences and user_preferences.get('search_description'):
            preferences_context = f"\nCandidate's Job Search Goals: {user_preferences['search_description']}"
        
        prompt = f"""Write a professional cover letter for this job application.

CANDIDATE'S RESUME:
{resume_text[:3000]}
{preferences_context}

JOB POSTING:
{job_details}

Instructions:
- Professional but conversational tone
- 3-4 paragraphs maximum
- Highlight relevant skills and experience from the resume
- Show enthusiasm for the specific role and company
- Explain why they're a good fit
- Include a strong opening and closing
- DO NOT make up experience or skills not in the resume
- Format with proper paragraphs (no "Dear Hiring Manager" salutation)

Write the cover letter body only (starting with the opening paragraph):"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Premium model for quality cover letters
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        cover_letter = message.content[0].text.strip()
        
        return cover_letter
        
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return f"Error generating cover letter: {str(e)}"
