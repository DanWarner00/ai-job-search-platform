"""
Resume parser using AI to extract text and skills from PDF/DOCX
"""
import PyPDF2
import os


def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        with open(filepath, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return None


def parse_resume(filepath):
    """
    Parse resume and extract text
    Returns the full text content
    """
    if not os.path.exists(filepath):
        return None
    
    # Extract text based on file type
    if filepath.endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
    elif filepath.endswith('.docx'):
        # TODO: Add DOCX support with python-docx library
        text = "DOCX parsing not yet implemented"
    else:
        return None
    
    return text
