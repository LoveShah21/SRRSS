# models/scorer.py
# Phase 4 – Cosine Similarity Scoring
# Phase 5 – Skill Extraction & Matching
# Phase 6 – Experience Matching
# Phase 7 – Final Weighted Scoring

from __future__ import annotations

import re
import logging
import numpy as np
from dataclasses import dataclass, field
from sklearn.metrics.pairwise import cosine_similarity

from utils.skill_dict import ALL_SKILLS_UNIQUE, normalize_skill

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SkillMatchResult:
    jd_skills: list[str]
    resume_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    skill_score: float          # 0.0 – 1.0


@dataclass
class ExperienceMatchResult:
    jd_years_required: float | None     # years extracted from JD
    resume_years_found: float | None    # years extracted from resume
    experience_score: float             # 0.0 – 1.0
    note: str


@dataclass
class ScoringResult:
    candidate_name: str
    filename: str
    similarity_score: float         # cosine similarity (0–1)
    skill_match: SkillMatchResult
    experience_match: ExperienceMatchResult
    final_score: float              # weighted (0–1)
    final_score_pct: float          # 0–100
    rank: int = 0                   # set later by ranker


# ──────────────────────────────────────────────────────────────────────────────
# Phase 4 – Cosine Similarity
# ──────────────────────────────────────────────────────────────────────────────

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Cosine similarity between two 1-D embedding vectors.
    Since embeddings are L2-normalised, this is simply the dot product.
    Returns a float in [0, 1] (embeddings are normalised, so values are ≥ 0).
    """
    # reshape for sklearn: (1, dim) each
    sim = cosine_similarity(vec_a.reshape(1, -1), vec_b.reshape(1, -1))
    score = float(sim[0][0])
    # Clamp to [0, 1] (floating-point safety)
    return max(0.0, min(1.0, score))


# ──────────────────────────────────────────────────────────────────────────────
# Phase 5 – Skill Extraction & Matching
# ──────────────────────────────────────────────────────────────────────────────

def extract_skills(text: str) -> list[str]:
    """
    Extract skills from a text by matching against the master skill dictionary.

    Uses multi-word phrase matching (e.g. "machine learning", "natural language processing")
    as well as single-word matching.

    Returns a deduplicated list of canonical skill names found in the text.
    """
    text_lower = text.lower()
    found: set[str] = set()

    # Sort by length descending so multi-word skills match before their sub-words
    sorted_skills = sorted(ALL_SKILLS_UNIQUE, key=len, reverse=True)

    for skill in sorted_skills:
        # Use word-boundary regex to avoid partial matches
        # e.g., "r" should not match inside "react" or "docker"
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            canonical = normalize_skill(skill)
            found.add(canonical)

    return sorted(found)


def compute_skill_score(resume_text: str, jd_text: str) -> SkillMatchResult:
    """
    Extract skills from both the resume and JD, then compute a skill match score.

    Score = |matched skills| / |JD skills|   (how many required skills are present)
    """
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)

    if not jd_skills:
        # No skills found in JD – give a neutral score
        return SkillMatchResult(
            jd_skills=[],
            resume_skills=resume_skills,
            matched_skills=[],
            missing_skills=[],
            skill_score=0.5,    # neutral when JD has no measurable skills
        )

    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    matched = sorted(jd_set & resume_set)
    missing = sorted(jd_set - resume_set)
    score = len(matched) / len(jd_set)

    return SkillMatchResult(
        jd_skills=jd_skills,
        resume_skills=resume_skills,
        matched_skills=matched,
        missing_skills=missing,
        skill_score=round(score, 4),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Phase 6 – Experience Matching
# ──────────────────────────────────────────────────────────────────────────────

# Patterns for extracting years of experience from text
_EXP_PATTERNS = [
    # "5+ years", "3-5 years", "at least 2 years"
    r"(\d+)\s*\+?\s*(?:to|-)\s*(\d+)\s*\+?\s*years?",   # range: 3-5 years
    r"(\d+)\s*\+\s*years?",                               # 5+ years
    r"(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp\.?)",  # "3 years of experience"
    r"(?:minimum|at\s+least|minimum\s+of)\s+(\d+)\s*years?",
    r"experience\s*[:\-–]?\s*(\d+)\s*years?",
    r"(\d+)\s*years?\s*(?:in|with|using)",
]

_RESUME_EXP_PATTERNS = [
    r"(\d{4})\s*(?:–|-|to)\s*(\d{4}|present|current|now)",  # "2019 – 2022"
    r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp\.?)",
    r"(?:total|overall)\s+(?:experience|exp\.?)\s*[:\-]?\s*(\d+)",
]


def _extract_years_from_text(text: str, patterns: list[str]) -> float | None:
    """Extract the most prominent years-of-experience number from text."""
    text_lower = text.lower()
    candidates: list[float] = []

    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            groups = [g for g in match.groups() if g and g.isdigit()]
            if groups:
                # For ranges (e.g., "3-5 years"), take the minimum (JD requirement)
                candidates.append(float(min(int(g) for g in groups)))

    if not candidates:
        return None

    # Return the highest sensible value (< 40 years to filter noise)
    valid = [y for y in candidates if 0 < y < 40]
    return max(valid) if valid else None


def _estimate_resume_years_from_dates(resume_text: str) -> float | None:
    """
    Estimate total experience from date ranges in the resume.
    e.g. "2019 – 2022", "Jan 2018 – Present"
    """
    import datetime

    current_year = datetime.datetime.now().year
    text_lower = resume_text.lower()

    # Match year ranges: "2018 - 2021" or "2018 - present"
    date_range_pattern = r"(\d{4})\s*(?:–|-|to)\s*(\d{4}|present|current|now)"
    ranges: list[tuple[int, int]] = []

    for match in re.finditer(date_range_pattern, text_lower):
        start_str, end_str = match.group(1), match.group(2)
        try:
            start = int(start_str)
            end = current_year if end_str in ("present", "current", "now") else int(end_str)
            if 1980 <= start <= current_year and start <= end <= current_year + 1:
                ranges.append((start, end))
        except ValueError:
            continue

    if not ranges:
        return None

    # Merge overlapping ranges to avoid double-counting
    ranges.sort()
    merged: list[tuple[int, int]] = [ranges[0]]
    for start, end in ranges[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    total_years = sum(end - start for start, end in merged)
    return float(total_years) if total_years > 0 else None


def compute_experience_score(resume_text: str, jd_text: str) -> ExperienceMatchResult:
    """
    Compare candidate experience against JD requirements.

    Scoring logic:
        - If JD requires N years and resume has >= N → score 1.0
        - If resume has (N - 1) years                → score 0.8
        - If resume has (N - 2) years                → score 0.5
        - Below that                                 → score 0.2
        - If no JD requirement found                 → neutral 0.7
    """
    jd_years = _extract_years_from_text(jd_text, _EXP_PATTERNS)
    resume_years = _extract_years_from_text(resume_text, _RESUME_EXP_PATTERNS)

    # If explicit years not found in resume, try inferring from date ranges
    if resume_years is None:
        resume_years = _estimate_resume_years_from_dates(resume_text)

    if jd_years is None:
        return ExperienceMatchResult(
            jd_years_required=None,
            resume_years_found=resume_years,
            experience_score=0.7,
            note="No explicit experience requirement found in JD. Neutral score applied.",
        )

    if resume_years is None:
        return ExperienceMatchResult(
            jd_years_required=jd_years,
            resume_years_found=None,
            experience_score=0.4,
            note="Could not determine candidate's years of experience from resume.",
        )

    gap = jd_years - resume_years
    if gap <= 0:
        score, note = 1.0, f"Meets requirement ({resume_years:.0f} ≥ {jd_years:.0f} yrs)."
    elif gap <= 1:
        score, note = 0.8, f"Slightly below requirement ({resume_years:.0f}/{jd_years:.0f} yrs)."
    elif gap <= 2:
        score, note = 0.5, f"Below requirement by ~2 years ({resume_years:.0f}/{jd_years:.0f} yrs)."
    else:
        score, note = 0.2, f"Significantly below requirement ({resume_years:.0f}/{jd_years:.0f} yrs)."

    return ExperienceMatchResult(
        jd_years_required=jd_years,
        resume_years_found=resume_years,
        experience_score=score,
        note=note,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Phase 7 – Final Scoring
# ──────────────────────────────────────────────────────────────────────────────

# Weights must sum to 1.0
WEIGHTS = {
    "similarity": 0.60,   # semantic similarity (embedding cosine)
    "skill":      0.25,   # skill match
    "experience": 0.15,   # experience match
}


def compute_final_score(
    similarity_score: float,
    skill_score: float,
    experience_score: float,
    weights: dict[str, float] | None = None,
) -> float:
    """
    Weighted combination of the three sub-scores.

    Args:
        similarity_score:  Cosine similarity between resume and JD embeddings (0–1).
        skill_score:       Fraction of JD skills found in resume (0–1).
        experience_score:  Experience match score (0–1).
        weights:           Custom weights dict (optional). Defaults to WEIGHTS above.

    Returns:
        Final score in [0, 1].
    """
    w = weights or WEIGHTS
    score = (
        w["similarity"] * similarity_score
        + w["skill"] * skill_score
        + w["experience"] * experience_score
    )
    return round(max(0.0, min(1.0, score)), 4)


def score_resume(
    resume_text: str,
    jd_text: str,
    resume_embedding: np.ndarray,
    jd_embedding: np.ndarray,
    filename: str = "resume.pdf",
    candidate_name: str = "Unknown",
) -> ScoringResult:
    """
    End-to-end scoring of a single resume against a job description.

    Steps:
        1. Cosine similarity (Phase 4)
        2. Skill extraction & matching (Phase 5)
        3. Experience matching (Phase 6)
        4. Weighted final score (Phase 7)

    Returns:
        ScoringResult dataclass with all sub-scores and matched/missing skills.
    """
    # Phase 4
    similarity = compute_cosine_similarity(resume_embedding, jd_embedding)

    # Phase 5
    skill_result = compute_skill_score(resume_text, jd_text)

    # Phase 6
    exp_result = compute_experience_score(resume_text, jd_text)

    # Phase 7
    final = compute_final_score(
        similarity_score=similarity,
        skill_score=skill_result.skill_score,
        experience_score=exp_result.experience_score,
    )

    return ScoringResult(
        candidate_name=candidate_name,
        filename=filename,
        similarity_score=round(similarity, 4),
        skill_match=skill_result,
        experience_match=exp_result,
        final_score=final,
        final_score_pct=round(final * 100, 2),
    )