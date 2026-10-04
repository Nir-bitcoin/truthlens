# parser.py
# Kaam: Har format support karo — PDF, DOCX, TXT, Images (OCR)

import pdfplumber
from docx import Document
from langdetect import detect, DetectorFactory
from PIL import Image
import pytesseract
import os

# Tesseract path (Windows ke liye)
# Agar Tesseract install hai to ye path sahi hai
# Agar nahi install, to error aayega — install karo pehle
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except Exception:
    pass

DetectorFactory.seed = 0


def parse_pdf(file_path):
    # PDF se text nikalta hai (page numbers ke saath)
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            # Agar text nahi mila to OCR try karo (scanned PDF)
            if not text.strip():
                try:
                    img = page.to_image(resolution=300)
                    text = pytesseract.image_to_string(img.original)
                except Exception:
                    text = ""

            if text.strip():
                pages.append({"page": i, "text": text})
    return pages


def parse_docx(file_path):
    # DOCX se text nikalta hai
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return [{"page": 1, "text": full_text}]


def parse_txt(file_path):
    # TXT se text nikalta hai
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [{"page": 1, "text": text}]


def parse_image(file_path):
    # Image se OCR karta hai
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return [{"page": 1, "text": text}]
    except Exception:
        return []


def detect_language(text):
    # Text ki language detect karta hai
    try:
        return detect(text[:500])
    except Exception:
        return "en"


def parse_document(file_path):
    # Main function: koi bhi file parse karo
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        pages = parse_pdf(file_path)
    elif ext == ".docx":
        pages = parse_docx(file_path)
    elif ext == ".txt":
        pages = parse_txt(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        pages = parse_image(file_path)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    full_text = " ".join([p["text"] for p in pages])
    lang = detect_language(full_text)

    return {
        "file": os.path.basename(file_path),
        "pages": pages,
        "language": lang,
        "full_text": full_text
    }


# Test karne ke liye
if __name__ == "__main__":
    result = parse_document("data/uploads/contract.txt")
    print(f"File: {result['file']}")
    print(f"Language: {result['language']}")
    print(f"Pages: {len(result['pages'])}")