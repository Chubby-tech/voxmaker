import re

def clean_text(text: str) -> str:
    """
    Cleans weird symbols, broken sentences, extra spaces, and page numbers.
    """
    # Remove simple page numbers (e.g., standalone digits on a line or common page formats)
    text = re.sub(r'(?i)^\s*(page\s*)?\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Replace weird symbols and non-ascii characters that might break TTS
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Fix broken sentences (e.g., words broken by hyphens across lines)
    text = re.sub(r'-\n\s*', '', text)
    
    # Replace multiple newlines with a single newline or double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
