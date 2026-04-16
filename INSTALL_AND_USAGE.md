# PDF Extractor — Install & Usage

This guide explains how to install, run, and test the PDF Date Extractor FastAPI service, and gives a short architecture overview.

1) Prerequisites (macOS)

- Homebrew (recommended)
- Python 3.10+ and git
- System packages for OCR and PDF rasterization:

```bash
brew install tesseract poppler
```

2) Python environment and dependencies

```bash
cd /Users/akshayskashyap/Documents/pdf-extractor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) Environment variables

Copy the example and edit as needed:

```bash
cp .env.example .env
# set LLM_API_URL and LLM_API_KEY if you have an external LLM; otherwise leave blank to use a local HF model
```

4) Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5) Generate sample PDFs (optional)

```bash
python tools/generate_sample_pdf.py
python tools/generate_complex_pdf.py
```

6) Test endpoints

Upload a file (returns `job_id`):

```bash
curl -s -X POST "http://localhost:8000/process" \
  -F "file=@data/complex_sample_dates.pdf" \
  -F "document_type=Complex Sample" | jq .
```

Poll job result:

```bash
curl -s "http://localhost:8000/jobs/<job_id>" | jq .
```

7) Where results and originals are stored

- Original uploads: `data/originals/`
- Job JSONs: `data/jobs/`

8) How it works (high level)

- API: `app/main.py` + `app/api/routes.py` — endpoints to upload and fetch jobs.
- OCR: `app/services/ocr.py` — digital PDF extraction with `pdfminer`; rasterization + Tesseract via `pdf2image` + `pytesseract` for scanned/handwritten images.
- LLM: `app/services/llm.py` — external LLM call if `LLM_API_URL` configured; otherwise falls back to a local Hugging Face model (if `transformers` installed) and heuristics.
- Processing: `app/processing/processor.py` — orchestrates extraction, classification, normalization, business-rule computation, validation, and job persistence.
- Storage and jobs: `app/services/storage.py`, `app/services/job_store.py` — save originals and job JSON files.
- Schemas: `app/schemas.py` — Pydantic models for structured output.

9) Notes & Troubleshooting

- First run with a local HF model may download model weights (slow). Pick a smaller model in `app/services/llm.py` if needed.
- If uploads fail with "Form data requires python-multipart", run `pip install python-multipart`.
- If OCR misses handwritten text, increase image DPI or pre-process images; consider using a better OCR engine for handwriting.
- If `git push` fails with SSH permission denied, follow SSH key setup or switch to HTTPS remote.

10) Next improvements

- Add canonicalization & provenance-aware confidence (we have a TODO for this).
- Add integration tests and CI workflows.
