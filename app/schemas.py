from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ExtractedDate(BaseModel):
    label: Optional[str]
    raw_text: str
    normalized: Optional[str]
    confidence: Confidence
    reasoning: Optional[str]


class ComputedDates(BaseModel):
    manufacturing_date: Optional[str]
    expiry_date: Optional[str]
    is_expired: Optional[bool]
    days_to_expiry: Optional[int]
    shelf_life_remaining: Optional[str]


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    needs_review = "needs_review"
    failed = "failed"


class JobResult(BaseModel):
    job_id: str
    status: JobStatus
    document_type: Optional[str]
    extracted_dates: List[ExtractedDate]
    computed: ComputedDates
    overall_confidence: Confidence
