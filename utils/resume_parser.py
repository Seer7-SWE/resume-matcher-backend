import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text if text.strip() else None  # Ensure non-empty text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None
