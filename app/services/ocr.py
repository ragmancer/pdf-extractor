from typing import List
import re
from pdfminer.high_level import extract_text as pdf_extract_text

from PIL import Image
import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(path: str) -> str:
    # Try digital text extraction first
    text = ""
    try:
        text = pdf_extract_text(path)
    except Exception:
        text = ""
    if text and len(text.strip()) > 20:
        return text

    # Fallback: rasterize pages and run Tesseract
    try:
        pages = convert_from_path(path)
        ocr_pages = [pytesseract.image_to_string(p) for p in pages]
        return "\n".join(ocr_pages)
    except Exception:
        return text


def extract_text_from_image(path: str) -> str:
    try:
        img = Image.open(path)
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


date_regex = re.compile(r"\b(?:\d{1,2}[\-/\. ]\d{1,2}[\-/\. ]\d{2,4}|\d{4}[\-/]\d{1,2}[\-/]\d{1,2}|[A-Za-z]{3,9} \d{1,2},? \d{4})\b")


def find_date_candidates(text: str) -> List[str]:
    return list({m.group(0) for m in date_regex.finditer(text)})


def ocr_extract(path: str) -> dict:
    # Detect by extension whether path is an image
    lower = path.lower()
    if lower.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp')):
        text = extract_text_from_image(path)
    else:
        text = extract_text_from_pdf(path)

    candidates = find_date_candidates(text)
    return {"text": text, "candidates": candidates}
