from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_invalid_extension():
    """BE-02: Uploading .txt file returns 400 with error message."""
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"invalid content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Недопустимый формат" in response.json()["detail"]

def test_upload_large_file():
    """BE-02: File >20MB returns 400."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(b"x" * (21 * 1024 * 1024))
        f.flush()
        with open(f.name, "rb") as file:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("large.docx", file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )
    assert response.status_code == 400
    assert "превышает 20 МБ" in response.json()["detail"]

def test_chunk_text():
    """BE-05: Text chunking produces correct segments with overlap."""
    from app.services.parser import chunk_text
    text = "a" * 2500
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) > 1
    assert len(chunks[0]["text"]) <= 1000
    assert len(chunks[1]["text"]) <= 1000

def test_parse_docx():
    """BE-04: DOCX parsing extracts text."""
    from app.services.parser import parse_docx
    import tempfile
    from docx import Document
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        doc = Document()
        doc.add_paragraph("Тестовый текст для парсинга")
        doc.save(f.name)
        result = parse_docx(f.name)
    assert "Тестовый текст" in result
