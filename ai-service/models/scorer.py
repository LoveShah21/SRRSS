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

# Patterns for extracting required years from a JD
_EXP_PATTERNS = [
    r"(\d+)\s*\+?\s*(?:to|-)\s*(\d+)\s*\+?\s*years?",          # "3-5 years"
    r"(\d+)\s*\+\s*years?",                                      # "5+ years"
    r"(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp\.?)",         # "3 years of experience"
    r"(?:minimum|at\s+least|minimum\s+of)\s+(\d+)\s*years?",
    r"experience\s*[:\-–]?\s*(\d+)\s*years?",
    r"(\d+)\s*years?\s*(?:in|with|using)",
]

# Explicit "X years of experience" patterns for resume (no date ranges here)
_RESUME_EXPLICIT_EXP_PATTERNS = [
    r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp\.?)",
    r"(?:total|overall)\s+(?:experience|exp\.?)\s*[:\-]?\s*(\d+)",
]

# ── Section classification regexes ────────────────────────────────────────────

# Headers that mark a WORK EXPERIENCE section
_WORK_SECTION_RE = re.compile(
    r"^\s*(work\s*experience|professional\s*experience|employment(\s*history)?|"
    r"experience|career(\s*history)?|work\s*history|job\s*history)\s*$",
    re.IGNORECASE,
)

# Headers that mark sections we must SKIP (education, projects, skills, etc.)
_NON_WORK_SECTION_RE = re.compile(
    r"^\s*(education|academic|qualification|schooling|projects?|"
    r"skills?|technical\s*skills?|coursework|certifications?|"
    r"achievements?|activities|languages?|profile|summary|objective|"
    r"position\s*of\s*responsibility|additional|volunteer|awards?|"
    r"interests?|hobbies|publications?|references?|database|"
    r"computer\s*languages?|note)\s*$",
    re.IGNORECASE,
)

# Generic section header detector (short line, only alpha + spaces)
_SECTION_HEADER_RE = re.compile(r"^\s*[A-Za-z][A-Za-z\s&/()]{2,45}\s*$")

# Month names for date parsing (full + abbreviated)
_MONTHS = (
    "january|february|march|april|may|june|july|august|september|"
    "october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec"
)

# Matches both:
#   Year-only  : "2021 – 2023"  /  "2021 - Present"
#   Month+Year : "June 2025 - Present"  /  "December 2024 - May 2025"
_DATE_RANGE_RE = re.compile(
    r"(?:(?:" + _MONTHS + r")\s+)?(\d{4})\s*(?:–|—|-|to)\s*"
    r"(?:(?:" + _MONTHS + r")\s+)?(\d{4}|present|current|now)",
    re.IGNORECASE,
)


def _extract_work_section_text(resume_text: str) -> str | None:
    """
    Isolate only the lines that belong to a work/professional experience section.

    Strategy:
      - Walk lines top-to-bottom tracking the current section.
      - A line is a section header if it matches _SECTION_HEADER_RE AND
        is short (≤ 50 chars) AND has no digits.
      - Collect lines only while inside a recognised work section.
      - Stop collecting when we enter a new, non-work section.

    Returns the collected text, or None if no work section was found.
    """
    lines = resume_text.split("\n")
    in_work_section = False
    work_lines: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Skip blank lines for header detection but keep them for content
        if not stripped:
            if in_work_section:
                work_lines.append(line)
            continue

        is_header = (
            _SECTION_HEADER_RE.match(stripped)
            and len(stripped) <= 50
            and not re.search(r"\d", stripped)   # headers don't contain digits
        )

        if is_header:
            if _WORK_SECTION_RE.match(stripped):
                in_work_section = True          # entered a work section
                continue                        # skip the header itself
            elif _NON_WORK_SECTION_RE.match(stripped):
                in_work_section = False         # left work section
                continue
            else:
                # Unknown section header → leave work section if we were in one
                if in_work_section:
                    in_work_section = False
                continue

        if in_work_section:
            work_lines.append(line)

    return "\n".join(work_lines) if work_lines else None


def _extract_years_from_text(text: str, patterns: list[str]) -> float | None:
    """Extract the most prominent years-of-experience number from text."""
    text_lower = text.lower()
    candidates: list[float] = []

    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            groups = [g for g in match.groups() if g and g.isdigit()]
            if groups:
                candidates.append(float(min(int(g) for g in groups)))

    valid = [y for y in candidates if 0 < y < 40]
    return max(valid) if valid else None


_MONTH_MAP = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6,
    "july": 7, "jul": 7, "august": 8, "aug": 8, "september": 9, "sep": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}


def _years_from_date_ranges(text: str) -> float | None:
    """
    Sum non-overlapping date ranges found in `text`, with month-level precision.
    Handles both "2021 - 2023" and "June 2025 - Present" formats.
    Only call this on text already confirmed to be from a work section.
    """
    import datetime
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month

    # Store ranges as (year*12 + month) for month-level precision
    ranges: list[tuple[int, int]] = []

    text_lower = text.lower()

    # Find all month+year or year-only date ranges
    # Pattern captures optional month before each year
    full_pattern = re.compile(
        r"((?:" + _MONTHS + r")\s+)?(\d{4})\s*(?:–|—|-|to)\s*"
        r"((?:" + _MONTHS + r")\s+)?(\d{4}|present|current|now)",
        re.IGNORECASE,
    )

    for match in full_pattern.finditer(text_lower):
        start_month_str = (match.group(1) or "").strip()
        start_year_str  = match.group(2)
        end_month_str   = (match.group(3) or "").strip()
        end_year_str    = match.group(4)

        try:
            start_year  = int(start_year_str)
            start_month = _MONTH_MAP.get(start_month_str, 1)  # default Jan

            if end_year_str.lower() in ("present", "current", "now"):
                end_year  = current_year
                end_month = current_month
            else:
                end_year  = int(end_year_str)
                end_month = _MONTH_MAP.get(end_month_str, 12)  # default Dec

            if not (1980 <= start_year <= current_year):
                continue
            if end_year < start_year:
                continue

            start_abs = start_year * 12 + start_month
            end_abs   = end_year   * 12 + end_month

            if start_abs <= end_abs:
                ranges.append((start_abs, end_abs))

        except ValueError:
            continue

    if not ranges:
        return None

    # Merge overlapping ranges
    ranges.sort()
    merged: list[tuple[int, int]] = [ranges[0]]
    for start, end in ranges[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    # Sum total months, convert to years (rounded to 1 decimal)
    total_months = sum(end - start for start, end in merged)
    total_years  = round(total_months / 12, 1)
    return total_years if total_years > 0 else None


def _years_from_month_year_ranges(resume_text: str) -> float | None:
    """
    Fallback: scan the FULL resume text but ONLY count date ranges that have
    a month name on at least one end (e.g. "June 2025 - Present",
    "December 2024 - May 2025").

    Rationale:
      - Education dates are almost always year-only: "2022 - 2025"
      - Work experience dates commonly include month names
      - So month+year ranges anywhere in the resume are reliably work experience

    This handles resumes where job entries appear before any section header
    or where the "EXPERIENCE" label is used for skills instead of work history.
    """
    import datetime
    now = datetime.datetime.now()
    current_year  = now.year
    current_month = now.month

    ranges: list[tuple[int, int]] = []
    text_lower = resume_text.lower()

    # Only match ranges where at least ONE side has a month name
    month_year_pattern = re.compile(
        r"((?:" + _MONTHS + r")\s+)(\d{4})\s*(?:–|—|-|to)\s*"
        r"((?:" + _MONTHS + r")\s+)?(\d{4}|present|current|now)",
        re.IGNORECASE,
    )

    for match in month_year_pattern.finditer(text_lower):
        start_month_str = (match.group(1) or "").strip()
        start_year_str  = match.group(2)
        end_month_str   = (match.group(3) or "").strip()
        end_year_str    = match.group(4)

        try:
            start_year  = int(start_year_str)
            start_month = _MONTH_MAP.get(start_month_str, 1)

            if end_year_str.lower() in ("present", "current", "now"):
                end_year  = current_year
                end_month = current_month
            else:
                end_year  = int(end_year_str)
                end_month = _MONTH_MAP.get(end_month_str, 12)

            if not (1980 <= start_year <= current_year):
                continue
            if end_year < start_year:
                continue

            start_abs = start_year * 12 + start_month
            end_abs   = end_year   * 12 + end_month

            if start_abs <= end_abs:
                ranges.append((start_abs, end_abs))

        except ValueError:
            continue

    if not ranges:
        return None

    ranges.sort()
    merged: list[tuple[int, int]] = [ranges[0]]
    for start, end in ranges[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    total_months = sum(end - start for start, end in merged)
    total_years  = round(total_months / 12, 1)
    return total_years if total_years > 0 else None


def compute_experience_score(resume_text: str, jd_text: str) -> ExperienceMatchResult:
    """
    Compare candidate experience against JD requirements.

    Resume years detection priority:
      1. Explicit "X years of experience" phrase anywhere in resume.
      2. Date ranges found ONLY inside a work/employment section header.
      3. If neither found → treat as fresher (0 years).

    Scoring:
        resume >= jd_required        → 1.0
        gap == 1 year                → 0.8
        gap == 2 years               → 0.5
        gap > 2 years / fresher      → 0.2
        no JD requirement            → 0.7 (neutral)
    """
    jd_years = _extract_years_from_text(jd_text, _EXP_PATTERNS)

    # Priority 1: explicit "X years of experience" in resume
    resume_years = _extract_years_from_text(resume_text, _RESUME_EXPLICIT_EXP_PATTERNS)

    # Priority 2: date ranges from work section (if a labeled section exists)
    if resume_years is None:
        work_text = _extract_work_section_text(resume_text)
        if work_text:
            resume_years = _years_from_date_ranges(work_text)

    # Priority 3: fallback — scan full resume for Month+Year date ranges.
    # Education dates are almost always year-only (e.g. "2022 - 2025").
    # Month+year patterns like "June 2025 - Present" are reliably work experience,
    # so we only pick up ranges that include a month name on at least one side.
    if resume_years is None:
        resume_years = _years_from_month_year_ranges(resume_text)

    # ── No JD requirement ──────────────────────────────────────────────────
    if jd_years is None:
        return ExperienceMatchResult(
            jd_years_required=None,
            resume_years_found=resume_years if resume_years is not None else 0.0,
            experience_score=0.7,
            note="No explicit experience requirement in JD. Neutral score applied.",
        )

    # ── Fresher / no experience found ─────────────────────────────────────
    if resume_years is None or resume_years == 0.0:
        return ExperienceMatchResult(
            jd_years_required=jd_years,
            resume_years_found=0.0,
            experience_score=0.2,
            note=(
                f"No professional work experience found in resume (fresher). "
                f"JD requires {jd_years:.0f} yr(s)."
            ),
        )

    # ── Compare — percentage-based scoring ───────────────────────────────
    # ratio = what % of the required years the candidate has
    # e.g. 3 yrs / 4 required = 0.75 → 75% → score 0.8
    # This is fairer than fixed gaps: a 2-yr gap means very different
    # things when JD requires 3 yrs vs 10 yrs.
    ratio = resume_years / jd_years   # always > 0 since resume_years > 0 here

    if ratio >= 1.0:
        score = 1.0
        note = (f"Meets requirement ({resume_years:.1f} ≥ {jd_years:.0f} yrs).")
    elif ratio >= 0.75:
        score = 0.8
        note = (f"Meets 75%+ of requirement ({resume_years:.1f}/{jd_years:.0f} yrs "
                f"→ {ratio*100:.0f}%).")
    elif ratio >= 0.50:
        score = 0.6
        note = (f"Meets 50–75% of requirement ({resume_years:.1f}/{jd_years:.0f} yrs "
                f"→ {ratio*100:.0f}%).")
    elif ratio >= 0.25:
        score = 0.4
        note = (f"Meets 25–50% of requirement ({resume_years:.1f}/{jd_years:.0f} yrs "
                f"→ {ratio*100:.0f}%).")
    else:
        score = 0.2
        note = (f"Meets less than 25% of requirement ({resume_years:.1f}/{jd_years:.0f} yrs "
                f"→ {ratio*100:.0f}%).")

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