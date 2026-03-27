"""
Data contracts for the entire pipeline.

Resume  ──┐
          ├──► FeatureVector ──► ScoreResult
JobReq  ──┘

List[Resume] + JobReq ──► RankResult
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enumerations ──────────────────────────────────────────────────────────────

class DegreeLevel(int, Enum):
    """
    Ordinal encoding so we can do numeric comparisons.
    Higher value = higher degree.
    """
    NONE        = 0
    DIPLOMA     = 1
    BACHELORS   = 2
    MASTERS     = 3
    PHD         = 4


class ExperienceLevel(str, Enum):
    ENTRY  = "entry"      # 0–2 yrs
    MID    = "mid"        # 2–5 yrs
    SENIOR = "senior"     # 5–10 yrs
    LEAD   = "lead"       # 10+ yrs


# ── Resume building blocks ────────────────────────────────────────────────────

class WorkExperience(BaseModel):
    company:          str
    title:            str
    years:            float = Field(..., ge=0.0, description="Duration in years")
    description:      str   = Field(..., min_length=10, description="Role responsibilities and achievements")
    skills_used:      list[str] = Field(default_factory=list)

    @field_validator("years")
    @classmethod
    def round_years(cls, v: float) -> float:
        return round(v, 1)


class Education(BaseModel):
    degree_level:    DegreeLevel
    field_of_study:  str
    institution:     str
    cgpa:            Optional[float] = Field(default=None, ge=0.0, le=10.0,
                                             description="CGPA on a 10-point scale; convert 4-point GPA externally")
    year_of_passing: Optional[int]   = Field(default=None, ge=1950, le=2100)


# ── Core Input Models ─────────────────────────────────────────────────────────

class Resume(BaseModel):
    """Structured resume — the canonical input on the candidate side."""
    candidate_id:       str
    name:               str
    email:              Optional[str]  = None
    professional_summary: str          = Field(..., min_length=20,
                                               description="2–4 sentence overview of the candidate")
    total_years_experience: float      = Field(..., ge=0.0)
    skills:             list[str]      = Field(..., min_length=1,
                                               description="Flat list of all technical and soft skills")
    work_experience:    list[WorkExperience] = Field(..., min_length=1)
    education:          list[Education]     = Field(..., min_length=1)

    @field_validator("skills")
    @classmethod
    def normalise_skills(cls, v: list[str]) -> list[str]:
        """Lowercase and strip whitespace so downstream matching is consistent."""
        return [s.strip().lower() for s in v if s.strip()]

    @model_validator(mode="after")
    def cross_check_experience(self) -> Resume:
        """total_years_experience must be consistent with work_experience entries."""
        derived = sum(w.years for w in self.work_experience)
        # Allow a ±2 year tolerance (gaps, overlaps, freelance etc.)
        if abs(self.total_years_experience - derived) > 2.0:
            raise ValueError(
                f"total_years_experience ({self.total_years_experience}) "
                f"differs from sum of work entries ({derived:.1f}) by more than 2 years."
            )
        return self

    @property
    def combined_work_text(self) -> str:
        """All work descriptions concatenated — used for semantic JD matching."""
        return " ".join(w.description for w in self.work_experience)

    @property
    def highest_degree(self) -> Education:
        return max(self.education, key=lambda e: e.degree_level.value)


class JobRequirement(BaseModel):
    """Structured job description — the canonical input on the job side."""
    job_id:                   str
    title:                    str
    description:              str  = Field(..., min_length=50,
                                           description="Full job description text")
    mandatory_skills:         list[str] = Field(..., min_length=1,
                                                description="Must-have skills; candidate penalised heavily for missing these")
    preferred_skills:         list[str] = Field(default_factory=list,
                                                description="Nice-to-have; adds to score but not required")
    bonus_skills:             list[str] = Field(default_factory=list,
                                                description="Differentiators that push score above threshold")
    min_years_experience:     float     = Field(..., ge=0.0)
    preferred_years_experience: float   = Field(..., ge=0.0)
    required_degree:          DegreeLevel = DegreeLevel.BACHELORS
    preferred_fields_of_study: list[str] = Field(default_factory=list)
    experience_level:         ExperienceLevel = ExperienceLevel.MID
    responsibilities:         list[str]  = Field(default_factory=list,
                                                  description="Key responsibilities; used for semantic similarity")

    @field_validator("mandatory_skills", "preferred_skills", "bonus_skills")
    @classmethod
    def normalise_skills(cls, v: list[str]) -> list[str]:
        return [s.strip().lower() for s in v if s.strip()]

    @model_validator(mode="after")
    def check_experience_range(self) -> JobRequirement:
        if self.preferred_years_experience < self.min_years_experience:
            raise ValueError(
                "preferred_years_experience must be >= min_years_experience"
            )
        return self


# ── Feature Vector (internal — produced by features.py) ──────────────────────

class FeatureVector(BaseModel):
    """
    16 numeric features extracted for one (resume, job) pair.
    All values are in [0.0, 1.0] unless documented otherwise.
    """
    # Skill matching (Phase 3a)
    mandatory_skill_overlap:    float = Field(..., ge=0.0, le=1.0)
    preferred_skill_overlap:    float = Field(..., ge=0.0, le=1.0)
    bonus_skill_overlap:        float = Field(..., ge=0.0, le=1.0)
    skill_coverage_score:       float = Field(..., ge=0.0, le=1.0,
                                              description="Weighted combo of the three tier overlaps")

    # Semantic skill similarity (Phase 3b)
    skill_semantic_similarity:  float = Field(..., ge=0.0, le=1.0,
                                              description="Cosine similarity between resume skill embeddings and JD skill embeddings")

    # Experience scoring (Phase 3c)
    meets_min_experience:       float = Field(..., ge=0.0, le=1.0,
                                              description="1.0 if candidate meets min_years, else ratio")
    experience_ratio:           float = Field(..., ge=0.0, le=1.0,
                                              description="Candidate years / preferred years, capped at 1.0")
    work_relevance_score:       float = Field(..., ge=0.0, le=1.0,
                                              description="Embedding similarity of past work descriptions to JD responsibilities")

    # Education scoring (Phase 3d)
    degree_level_score:         float = Field(..., ge=0.0, le=1.0,
                                              description="Candidate degree ordinal / required degree ordinal, capped at 1.0")
    field_match_score:          float = Field(..., ge=0.0, le=1.0,
                                              description="Semantic similarity of field of study to preferred fields")
    cgpa_score:                 float = Field(..., ge=0.0, le=1.0,
                                              description="CGPA / 10.0; 0.5 if not provided")

    # Semantic JD matching (Phase 3e)
    summary_jd_similarity:      float = Field(..., ge=0.0, le=1.0,
                                              description="Embedding cosine sim: professional_summary vs full JD")
    experience_jd_similarity:   float = Field(..., ge=0.0, le=1.0,
                                              description="Embedding cosine sim: combined work text vs full JD")
    skill_jd_similarity:        float = Field(..., ge=0.0, le=1.0,
                                              description="Embedding cosine sim: skill list vs JD responsibilities")

    # Aggregate signals
    overall_skill_score:        float = Field(..., ge=0.0, le=1.0,
                                              description="Blend of keyword overlap + semantic similarity")
    overall_semantic_score:     float = Field(..., ge=0.0, le=1.0,
                                              description="Average of the three semantic JD similarity scores")

    def to_list(self) -> list[float]:
        """Ordered feature list expected by the XGBoost model."""
        return [
            self.mandatory_skill_overlap,
            self.preferred_skill_overlap,
            self.bonus_skill_overlap,
            self.skill_coverage_score,
            self.skill_semantic_similarity,
            self.meets_min_experience,
            self.experience_ratio,
            self.work_relevance_score,
            self.degree_level_score,
            self.field_match_score,
            self.cgpa_score,
            self.summary_jd_similarity,
            self.experience_jd_similarity,
            self.skill_jd_similarity,
            self.overall_skill_score,
            self.overall_semantic_score,
        ]

    @classmethod
    def feature_names(cls) -> list[str]:
        """Must stay in the same order as to_list()."""
        return [
            "mandatory_skill_overlap",
            "preferred_skill_overlap",
            "bonus_skill_overlap",
            "skill_coverage_score",
            "skill_semantic_similarity",
            "meets_min_experience",
            "experience_ratio",
            "work_relevance_score",
            "degree_level_score",
            "field_match_score",
            "cgpa_score",
            "summary_jd_similarity",
            "experience_jd_similarity",
            "skill_jd_similarity",
            "overall_skill_score",
            "overall_semantic_score",
        ]


# ── Output Models ─────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    """Per-component scores for explainability."""
    skill:      float = Field(..., ge=0.0, le=1.0)
    experience: float = Field(..., ge=0.0, le=1.0)
    education:  float = Field(..., ge=0.0, le=1.0)
    semantic:   float = Field(..., ge=0.0, le=1.0)


class ScoreResult(BaseModel):
    """API response for POST /api/v1/score"""
    candidate_id:   str
    job_id:         str
    score:          float          = Field(..., ge=0.0, le=1.0,
                                           description="Final score in [0.0, 1.0]")
    grade:          str            = Field(..., description="A+, A, B+, B, C, or D")
    breakdown:      ScoreBreakdown
    feature_vector: FeatureVector


class RankedCandidate(BaseModel):
    """Single entry in a ranked list."""
    rank:         int
    candidate_id: str
    name:         str
    score:        float = Field(..., ge=0.0, le=1.0)
    grade:        str


class RankStats(BaseModel):
    """Distribution statistics over all scored candidates in a batch."""
    total_candidates: int
    returned:         int
    mean_score:       float
    median_score:     float
    std_score:        float
    min_score:        float
    max_score:        float


class RankResult(BaseModel):
    """API response for POST /api/v1/rank"""
    job_id:     str
    candidates: list[RankedCandidate]
    stats:      RankStats


# ── API Request Models ────────────────────────────────────────────────────────

class ScoreRequest(BaseModel):
    resume: Resume
    job:    JobRequirement


class RankRequest(BaseModel):
    resumes: list[Resume] = Field(..., min_length=1)
    job:     JobRequirement
    top_n:   Optional[int]   = Field(default=None, ge=1,
                                     description="Return only top N candidates; None = return all")
    min_score: Optional[float] = Field(default=None, ge=0.0, le=1.0,
                                        description="Filter out candidates below this score")