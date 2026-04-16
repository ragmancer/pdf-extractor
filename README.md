# PDF Date Extractor - FastAPI Backend

AI-assisted pipeline for extracting, classifying, normalizing and computing dates from documents (PDFs, scanned images, handwritten). This repository contains a FastAPI backend scaffold with pluggable OCR/LLM/storage services and a deterministic date computation pipeline.

Quick start

1. Create and activate a Python virtualenv (macOS):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy environment variables:

```bash
cp .env.example .env
# edit .env to add API keys if available
```

3. Run the app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Example request (upload a file):

```bash
curl -F "file=@/path/to/doc.pdf" -F "document_type=Certificate of Analysis" http://localhost:8000/process
```

Get job:

```bash
curl http://localhost:8000/jobs/<job_id>
```

Notes
- OCR is local using `pdfminer`, `pytesseract`, and `pdf2image` (requires Tesseract and Poppler installed).
- The only external API expected is the LLM (configure `LLM_API_URL` and `LLM_API_KEY` in `.env`).

Local prerequisites (macOS):

```bash
brew install tesseract poppler
```

Local LLM options

- Option A (recommended small, CPU-friendly): `google/flan-t5-small` via `transformers` pipeline. Install deps with `pip install transformers torch sentencepiece` and the app will attempt to load this model automatically when no external `LLM_API_URL` is configured.
- Option B (faster/larger): run a local text-generation server (e.g., `text-generation-inference` or `llama.cpp` wrappers) and point `LLM_API_URL` to it.

If you don't configure `LLM_API_URL`/`LLM_API_KEY` the service will try to use a local Hugging Face model; otherwise it will call the external LLM.
