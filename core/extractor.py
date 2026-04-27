import os

def extract_text(file_path: str) -> str:
    """
    Extracts text from PDF, TXT, and DOCX files.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return _extract_pdf(file_path)
    elif ext == '.docx':
        return _extract_docx(file_path)
    elif ext == '.txt':
        return _extract_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def _extract_pdf(file_path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF files. Run 'pip install PyMuPDF'")
        
    doc = fitz.open(file_path)
    text = []
    for page in doc:
        text.append(page.get_text())
    return "\n".join(text)

def _extract_docx(file_path: str) -> str:
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required for DOCX files. Run 'pip install python-docx'")
        
    doc = Document(file_path)
    text = [para.text for para in doc.paragraphs]
    return "\n".join(text)

def _extract_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
