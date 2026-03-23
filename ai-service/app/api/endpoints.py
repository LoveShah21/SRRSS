from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
from docx import Document
import fitz

from app.nlp.parser import extract_entities
from app.nlp.bias import detect_biased_terms
from app.models.scorer import calculate_match_score

router = APIRouter()

class CandidateData(BaseModel):
    candidateSkills: List[str]
    candidateText: str

class ScoringRequest(BaseModel):
    jobText: str
    jobSkills: List[str]
    candidate: CandidateData

class BiasRequest(BaseModel):
    jobDescription: str


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page in document:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts).strip()


def _extract_text_from_docx(file_bytes: bytes) -> str:
    from io import BytesIO

    document = Document(BytesIO(file_bytes))
    return "\n".join([paragraph.text for paragraph in document.paragraphs]).strip()

@router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if file.content_type == "application/pdf":
        raw_text = _extract_text_from_pdf(file_bytes)
    else:
        raw_text = _extract_text_from_docx(file_bytes)

    entities = extract_entities(raw_text)
    response = {
        "filename": file.filename,
        "raw_text": raw_text[:12000],
        "extracted_data": {
            "name": entities.get("PERSON", [None])[0],
            "email": entities.get("EMAIL", [None])[0],
            "skills": entities.get("SKILLS", []),
            "education": entities.get("EDUCATION", []),
            "experience": entities.get("EXPERIENCE", []),
        }
    }
    return response

@router.post("/score-candidate")
async def score_candidate(payload: ScoringRequest):
    score = calculate_match_score(payload.jobText, payload.candidate.candidateText)
    normalized_job_skills = [skill.strip().lower() for skill in payload.jobSkills]
    normalized_candidate_skills = [skill.strip().lower() for skill in payload.candidate.candidateSkills]
    matched_skills = [skill for skill in normalized_candidate_skills if skill in normalized_job_skills]
    return {"match_score": score, "matched_skills": sorted(set(matched_skills))}

@router.post("/detect-bias")
async def detect_bias(payload: BiasRequest):
    return {
        "biased_words_found": detect_biased_terms(payload.jobDescription),
        "recommendation": "Consider replacing aggressive terminology to be more inclusive."
    }
