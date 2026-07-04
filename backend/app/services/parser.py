import pdfplumber
from docx import Document

def parse_document(file_path: str, ext: str) -> str:
    """Extract text from PDF or DOCX file."""
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    else:
        raise ValueError("Unsupported format: expected .pdf or .docx")

def parse_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def parse_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text])

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list:
    """Split text into overlapping chunks for indexing."""
    chunks = []
    start = 0
    page = 1
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append({"text": chunk, "page": page})
        start += chunk_size - overlap
        page += 1
    return chunks
