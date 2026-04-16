from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="PDF Date Extractor")

app.include_router(routes.router)

@app.get("/")
def root():
    return {"status": "ok"}
