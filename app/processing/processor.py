import uuid
from typing import List, Dict
from datetime import date
from app.services import ocr, llm, storage
from app.services.job_store import save_job
from app.config import settings
from app.utils.dates import normalize_date, add_months, days_between
from app.schemas import Confidence


def build_context(text: str, candidate: str, window: int = 80) -> str:
    idx = text.find(candidate)
    if idx == -1:
        return text[:window]
    start = max(0, idx - window)
    end = min(len(text), idx + len(candidate) + window)
    return text[start:end]


def compute_business_rules(label_map: Dict[str, str]) -> Dict:
    computed = {
        "manufacturing_date": None,
        "expiry_date": None,
        "is_expired": None,
        "days_to_expiry": None,
        "shelf_life_remaining": None,
    }
    mfg = label_map.get("manufacturing_date")
    exp = label_map.get("expiry_date")
    if mfg:
        computed["manufacturing_date"] = mfg
        if not exp:
            # default expiry rule = mfg + default_expiry_months
            exp = add_months(mfg, settings.default_expiry_months)
            computed["expiry_date"] = exp
        else:
            computed["expiry_date"] = exp

        today = date.today().isoformat()
        days = days_between(today, computed["expiry_date"]) if computed["expiry_date"] else None
        computed["days_to_expiry"] = days
        computed["is_expired"] = days is not None and days < 0
        if days is not None:
            computed["shelf_life_remaining"] = f"{days} days"

    return computed


def process_job(job_id: str, file_path: str, document_type: str | None = None):
    # Start processing
    job = {
        "job_id": job_id,
        "status": "processing",
        "document_type": document_type,
        "extracted_dates": [],
        "computed": {},
        "overall_confidence": "low",
    }
    save_job(job_id, job)

    try:
        ocr_res = ocr.ocr_extract(file_path)
        text = ocr_res.get("text", "")
        candidates: List[str] = ocr_res.get("candidates", [])

        label_map = {}
        extracted = []
        confidences = []

        for c in candidates:
            ctx = build_context(text, c)
            llm_res = llm.classify_and_disambiguate(c, ctx)
            label = llm_res.get("label")
            normalized_from_llm = llm_res.get("normalized")
            # prefer LLM-normalized value, otherwise deterministic parser
            normalized = normalized_from_llm or normalize_date(c)
            confidence = Confidence.high if normalized else Confidence.low
            reasoning = (
                f"LLM provided normalized={normalized_from_llm}; context snippet: {ctx[:80].strip()}"
                if normalized_from_llm
                else f"Found near words: {ctx[:80].strip()}"
            )
            extracted.append({
                "label": label,
                "raw_text": c,
                "normalized": normalized,
                "confidence": confidence,
                "reasoning": reasoning,
            })
            if normalized and label:
                label_map[label] = normalized
            confidences.append(confidence)

        computed = compute_business_rules(label_map)

        overall = Confidence.low
        if any(c == Confidence.high for c in confidences):
            overall = Confidence.medium
        if all(c == Confidence.high for c in confidences) and len(confidences) > 0:
            overall = Confidence.high

        status = "completed"
        if any(c == Confidence.low for c in confidences):
            status = "needs_review"

        job.update({
            "status": status,
            "extracted_dates": extracted,
            "computed": computed,
            "overall_confidence": overall,
        })
        save_job(job_id, job)
    except Exception as e:
        job.update({"status": "failed", "error": str(e)})
        save_job(job_id, job)
