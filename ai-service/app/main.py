from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(
    title="SRRSS AI Engine",
    description="Python microservice for Resume Parsing, Scoring, and Bias Detection.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "OK", "service": "SRRSS AI Engine"}
