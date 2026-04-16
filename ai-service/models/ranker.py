# models/ranker.py
# Phase 8 – Ranking System
# Orchestrates parsing → embedding → scoring → sorting for a batch of resumes
#
# GUARANTEE: Every resume uploaded is ALWAYS returned in the rankings.
# If parsing or scoring fails, the resume gets final_score=0.0 and is
# placed at the bottom with a clear explanatory note — never silently dropped.

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import numpy as np

from models.resume_parser import parse_resume
from models.preprocessor import preprocess_for_embedding
from models.embedder import get_embedding, get_embeddings_batch
from models.scorer import (
    score_resume, ScoringResult,
    SkillMatchResult, ExperienceMatchResult,
)

logger = logging.getLogger(__name__)


@dataclass
class ResumeFile:
    filename: str
    file_bytes: bytes
    candidate_name: str = ""   # Optional: extracted or provided by caller


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _extract_candidate_name(raw_text: str) -> str:
    """
    Heuristic: the candidate name is usually on the first 1-2 lines of the resume.
    Returns the first non-empty line as a best guess.
    """
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    if not lines:
        return "Unknown"
    for line in lines[:5]:
        if (
            2 < len(line) < 60
            and not re.search(r"\d", line)
            and not any(
                kw in line.lower()
                for kw in ["resume", "curriculum", "vitae", "cv", "profile",
                           "summary", "objective", "contact", "email"]
            )
        ):
            return line
    return lines[0][:60]


def _make_zero_score_result(rf: ResumeFile, reason: str) -> ScoringResult:
    """
    Build a ScoringResult with score=0 for a resume that could not be
    parsed or scored. Still included in the final rankings (at the bottom)
    with a clear note so the company knows what happened.
    """
    return ScoringResult(
        candidate_name=rf.candidate_name or rf.filename,
        filename=rf.filename,
        similarity_score=0.0,
        skill_match=SkillMatchResult(
            jd_skills=[],
            resume_skills=[],
            matched_skills=[],
            missing_skills=[],
            skill_score=0.0,
        ),
        experience_match=ExperienceMatchResult(
            jd_years_required=None,
            resume_years_found=0.0,
            experience_score=0.0,
            note=f"Could not process resume — {reason}",
        ),
        final_score=0.0,
        final_score_pct=0.0,
        rank=0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ──────────────────────────────────────────────────────────────────────────────

def rank_resumes(
    resume_files: list[ResumeFile],
    jd_text: str,
) -> list[ScoringResult]:
    """
    Full pipeline: parse → preprocess → embed → score → rank N resumes vs a JD.

    Every resume in resume_files is guaranteed to appear in the returned list.
    Parse / scoring failures produce a score=0 entry placed at the bottom.

    Args:
        resume_files:  List of ResumeFile objects (filename + raw bytes).
        jd_text:       Raw job description text.

    Returns:
        List of ScoringResult for ALL resumes, sorted by final_score descending.
    """
    if not resume_files:
        raise ValueError("No resume files provided.")
    if not jd_text.strip():
        raise ValueError("Job description text is empty.")

    # ── Step 1: Parse — never skip, collect failures as zero-score ────────
    logger.info("Parsing %d resume(s)...", len(resume_files))

    raw_texts: list[str] = []
    valid_files: list[ResumeFile] = []
    zero_score_results: list[ScoringResult] = []

    for rf in resume_files:
        try:
            raw = parse_resume(rf.file_bytes, rf.filename)
            if raw.strip():
                raw_texts.append(raw)
                valid_files.append(rf)
            else:
                # Parsed OK but got empty text — likely image-based PDF
                # (OCR support planned as future enhancement)
                reason = (
                    "no selectable text found. "
                    "This PDF may be image-based or scanned. "
                    "Please re-upload as a text-based PDF or DOCX."
                )
                logger.warning("Empty text from '%s' → zero-score entry.", rf.filename)
                zero_score_results.append(_make_zero_score_result(rf, reason))
        except Exception as e:
            reason = f"file could not be read ({type(e).__name__}: {e})"
            logger.error("Parse error for '%s': %s", rf.filename, e)
            zero_score_results.append(_make_zero_score_result(rf, reason))

    # ── Step 2: Extract candidate names for parseable resumes ─────────────
    for rf, raw in zip(valid_files, raw_texts):
        if not rf.candidate_name:
            rf.candidate_name = _extract_candidate_name(raw)

    # ── Steps 3-5: Preprocess → Embed → Score (parseable resumes only) ────
    scored_results: list[ScoringResult] = []

    if valid_files:
        # Preprocess
        logger.info("Preprocessing texts...")
        jd_for_embedding = preprocess_for_embedding(jd_text)
        resume_texts_for_embedding = [preprocess_for_embedding(t) for t in raw_texts]

        # Embed
        logger.info("Generating embeddings...")
        jd_embedding: np.ndarray = get_embedding(jd_for_embedding)

        if len(resume_texts_for_embedding) > 1:
            resume_embeddings = get_embeddings_batch(resume_texts_for_embedding)
        else:
            resume_embeddings = get_embedding(resume_texts_for_embedding[0]).reshape(1, -1)

        # Score — scoring errors also become zero-score entries
        logger.info("Scoring %d resume(s)...", len(valid_files))
        for rf, raw, embed in zip(valid_files, raw_texts, resume_embeddings):
            try:
                result = score_resume(
                    resume_text=raw,
                    jd_text=jd_text,
                    resume_embedding=embed,
                    jd_embedding=jd_embedding,
                    filename=rf.filename,
                    candidate_name=rf.candidate_name,
                )
                scored_results.append(result)
            except Exception as e:
                reason = f"scoring error ({type(e).__name__}: {e})"
                logger.error("Scoring failed for '%s': %s", rf.filename, e)
                zero_score_results.append(_make_zero_score_result(rf, reason))

    # ── Step 6: Merge → sort → assign ranks ──────────────────────────────
    # Scored resumes sorted by score descending; zero-score entries always last
    scored_results.sort(key=lambda r: r.final_score, reverse=True)
    all_results = scored_results + zero_score_results

    for rank, result in enumerate(all_results, start=1):
        result.rank = rank

    logger.info(
        "Ranking complete. %d scored | %d zero-score (parse/score failed) | %d total",
        len(scored_results), len(zero_score_results), len(all_results),
    )

    return all_results