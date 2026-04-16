import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from app.services.storage import save_original
from app.services.job_store import save_job, load_job
from app.processing.processor import process_job
from app.schemas import JobStatus

router = APIRouter()


@router.post("/process")
async def process_endpoint(background: BackgroundTasks, file: UploadFile = File(...), document_type: str | None = None):
    job_id = str(uuid.uuid4())
    # save incoming file
    filename = f"{job_id}_{file.filename}"
    file_path = save_original(file.file, filename)

    # initial job
    job = {
        "job_id": job_id,
        "status": JobStatus.pending,
        "document_type": document_type,
        "extracted_dates": [],
        "computed": {},
        "overall_confidence": "low",
    }
    save_job(job_id, job)

    # schedule processing in background
    background.add_task(process_job, job_id, file_path, document_type)

    return {"job_id": job_id, "status": "accepted"}


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = load_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job
