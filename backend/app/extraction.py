import io

import pypdf
from docx import Document
from fastapi import HTTPException, UploadFile

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def _extract_pdf(content: bytes) -> str: #pdf reader
    reader = pypdf.PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def _extract_docx(content: bytes) -> str: #docx reader
    document = Document(io.BytesIO(content))
    return "\n".join(p.text for p in document.paragraphs)

def extract_text(file: UploadFile) -> str: # handler for parsing files
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File is too large (max 5MB)")

    if file.content_type == "application/pdf":
        return _extract_pdf(content)
    if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _extract_docx(content)
    raise HTTPException(400, "Unsupported file type — upload a PDF or .docx file")