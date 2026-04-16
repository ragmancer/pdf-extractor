import json
from typing import Optional
import requests

from app.config import settings

_hf_pipeline = None


def heuristic_label(candidate: str, context: str) -> str:
    ctx = context.lower()
    if any(k in ctx for k in ["mfg", "manufact", "manufacturing", "mfd"]):
        return "manufacturing_date"
    if any(k in ctx for k in ["exp", "expiry", "expiration", "best before"]):
        return "expiry_date"
    if any(k in ctx for k in ["test", "tested", "analysis", "assay"]):
        return "testing_date"
    if any(k in ctx for k in ["ship", "shipped", "shipping"]):
        return "shipping_date"
    return "other"


def _init_hf_model(model_name: str = "google/flan-t5-small"):
    global _hf_pipeline
    if _hf_pipeline is not None:
        return _hf_pipeline
    try:
        from transformers import pipeline

        _hf_pipeline = pipeline("text2text-generation", model=model_name, device_map="auto")
        return _hf_pipeline
    except Exception:
        _hf_pipeline = None
        return None


def classify_and_disambiguate(candidate: str, context: str) -> dict:
    """
    Primary path: call external LLM endpoint if configured.
    Fallbacks:
    - If no external endpoint, attempt to use a local Hugging Face model (flan-t5-small by default).
    - If transformers not available or model loading fails, fall back to heuristics and no normalization.

    Returns {"label": str, "normalized": Optional[str]}
    """
    # 1) External LLM endpoint
    if settings.llm_api_url and settings.llm_api_key:
        try:
            payload = {
                "candidate": candidate,
                "context": context,
                "instructions": (
                    "Return a JSON object with keys 'label' and optionally 'normalized'. "
                    "'label' should be one of: manufacturing_date, expiry_date, testing_date, "
                    "shipping_date, other. 'normalized' if present should be an ISO date YYYY-MM-DD."
                ),
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.llm_api_key}",
            }
            resp = requests.post(settings.llm_api_url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                try:
                    j = resp.json()
                    return {"label": j.get("label") or heuristic_label(candidate, context), "normalized": j.get("normalized")}
                except Exception:
                    return {"label": heuristic_label(candidate, context), "normalized": None}
            else:
                return {"label": heuristic_label(candidate, context), "normalized": None}
        except Exception:
            return {"label": heuristic_label(candidate, context), "normalized": None}

    # 2) Try local HF model
    try:
        pipe = _init_hf_model()
        if pipe is not None:
            prompt = (
                "You are a JSON-producing assistant. Given a date-like text and surrounding context, "
                "return a JSON object with keys 'label' (one of manufacturing_date, expiry_date, testing_date, shipping_date, other) "
                "and optionally 'normalized' which should be an ISO date YYYY-MM-DD if you can confidently parse it.\n"
                f"candidate: {candidate}\ncontext: {context}\n\nRespond ONLY with JSON."
            )
            out = pipe(prompt, max_length=128)
            txt = out[0]["generated_text"] if isinstance(out, list) else str(out)
            # try to find JSON substring
            try:
                jtxt = txt.strip()
                # sometimes model returns text before JSON; find first '{'
                idx = jtxt.find('{')
                if idx != -1:
                    jtxt = jtxt[idx:]
                j = json.loads(jtxt)
                return {"label": j.get("label") or heuristic_label(candidate, context), "normalized": j.get("normalized")}
            except Exception:
                return {"label": heuristic_label(candidate, context), "normalized": None}
    except Exception:
        pass

    # 3) Fallback heuristic
    return {"label": heuristic_label(candidate, context), "normalized": None}

