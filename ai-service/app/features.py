"""
Feature Engineering — Phase 3

Converts a (Resume, JobRequirement) pair into a 16-dimensional FeatureVector.

Five sub-pipelines, executed in order:
  3a  Skill matching        — keyword overlap across mandatory / preferred / bonus tiers
  3b  Semantic skill sim    — cosine similarity between embedded skill lists
  3c  Experience scoring    — years comparison + work-description relevance
  3d  Education scoring     — degree level, field match, CGPA
  3e  Semantic JD matching  — summary / work-text / skills vs full JD

Public API
----------
  engine = EmbeddingEngine()                       # load once at startup
  fv     = extract_features(resume, job, engine)   # call per (resume, job) pair
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

from config import embedding_config, skill_weights, model_paths
from schemas import DegreeLevel, Education, FeatureVector, JobRequirement, Resume

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

# Built-in synonym map: maps abbreviations / aliases → canonical form.
# Loaded first; if ml/artifacts/synonyms.json exists it is merged on top.
_BUILTIN_SYNONYMS: dict[str, str] = {
    # Programming languages
    "js":             "javascript",
    "ts":             "typescript",
    "py":             "python",
    "rb":             "ruby",
    "golang":         "go",
    "c#":             "csharp",
    "c++":            "cpp",

    # ML / AI
    "ml":             "machine learning",
    "dl":             "deep learning",
    "ai":             "artificial intelligence",
    "nlp":            "natural language processing",
    "cv":             "computer vision",
    "rl":             "reinforcement learning",
    "llm":            "large language model",
    "gen ai":         "generative ai",
    "genai":          "generative ai",

    # Data / Engineering
    "sql":            "structured query language",
    "nosql":          "non-relational database",
    "etl":            "extract transform load",
    "elt":            "extract load transform",
    "bi":             "business intelligence",
    "dw":             "data warehouse",
    "de":             "data engineering",
    "ds":             "data science",
    "da":             "data analysis",

    # Cloud / Infra
    "aws":            "amazon web services",
    "gcp":            "google cloud platform",
    "k8s":            "kubernetes",
    "ci/cd":          "continuous integration continuous deployment",
    "cicd":           "continuous integration continuous deployment",
    "iac":            "infrastructure as code",

    # Web
    "fe":             "frontend",
    "be":             "backend",
    "fs":             "full stack",
    "ux":             "user experience",
    "ui":             "user interface",
    "rest":           "restful api",
    "api":            "application programming interface",
    "spa":            "single page application",

    # Soft skills
    "pm":             "project management",
    "agile/scrum":    "agile",
    "oop":            "object oriented programming",
    "tdd":            "test driven development",

    # Frameworks (common short forms)
    "tf":             "tensorflow",
    "pt":             "pytorch",
    "sk-learn":       "scikit-learn",
    "sklearn":        "scikit-learn",
    "hf":             "huggingface",

    # Databases
    "pg":             "postgresql",
    "mongo":          "mongodb",
    "es":             "elasticsearch",
    "mq":             "message queue",
}


# ── Text normalisation helpers ─────────────────────────────────────────────────

def _normalise_text(text: str) -> str:
    """
    Lowercase, strip accents, collapse whitespace.
    Keeps hyphens and slashes — used in compound skill names like "ci/cd".
    """
    text = text.lower().strip()
    # Unicode normalise: decompose then strip combining marks
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text


def _apply_synonyms(skill: str, synonym_map: dict[str, str]) -> str:
    """Replace a skill with its canonical form if a synonym entry exists."""
    normalised = _normalise_text(skill)
    return synonym_map.get(normalised, normalised)


def _load_synonym_map(path: Optional[Path] = None) -> dict[str, str]:
    """
    Start with the built-in map; merge project-level synonyms.json on top.
    Project-level entries override built-ins.
    """
    merged = dict(_BUILTIN_SYNONYMS)
    target = path or model_paths.synonyms_file
    if target.exists():
        try:
            with open(target) as f:
                custom: dict[str, str] = json.load(f)
            merged.update({k.lower().strip(): v.lower().strip()
                            for k, v in custom.items()})
            logger.debug("Loaded %d custom synonyms from %s", len(custom), target)
        except Exception as exc:
            logger.warning("Could not load synonyms file %s: %s", target, exc)
    return merged


# ── Embedding engine ───────────────────────────────────────────────────────────

class EmbeddingEngine:
    """
    Thin wrapper around sentence-transformers.
    Load once at application startup; reuse across all requests.

    Usage
    -----
        engine = EmbeddingEngine()
        vec    = engine.embed("machine learning engineer")
        sim    = engine.cosine_sim(vec_a, vec_b)
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
    ) -> None:
        self._model_name  = model_name or embedding_config.model_name
        self._device      = device     or embedding_config.device
        logger.info("Loading embedding model: %s on %s", self._model_name, self._device)
        self._model       = SentenceTransformer(self._model_name, device=self._device)
        self._synonym_map = _load_synonym_map()
        logger.info("EmbeddingEngine ready.")

    # ── Core embedding ─────────────────────────────────────────────────────────

    def embed(self, text: str) -> np.ndarray:
        """Embed a single string → L2-normalised 1-D float32 array."""
        return self._model.encode(
            text,
            batch_size=1,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """
        Embed a list of strings → 2-D array [N, dim].
        Each row is L2-normalised.
        """
        if not texts:
            dim = self._model.get_sentence_embedding_dimension()
            return np.zeros((0, dim), dtype=np.float32)
        return self._model.encode(
            texts,
            batch_size=embedding_config.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    # ── Similarity ─────────────────────────────────────────────────────────────

    @staticmethod
    def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        """
        Cosine similarity between two 1-D vectors, clipped to [0.0, 1.0].
        Handles normalised and non-normalised inputs.
        """
        na, nb = norm(a), norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.clip(np.dot(a, b) / (na * nb), 0.0, 1.0))

    def mean_pool_sim(self, texts_a: list[str], texts_b: list[str]) -> float:
        """
        Embed two lists of strings, mean-pool each group into one vector,
        then return cosine similarity between the two pooled vectors.
        Returns 0.0 if either list is empty.
        """
        if not texts_a or not texts_b:
            return 0.0
        embs_a = self.embed_batch(texts_a).mean(axis=0)   # [D]
        embs_b = self.embed_batch(texts_b).mean(axis=0)   # [D]
        return self.cosine_sim(embs_a, embs_b)

    # ── Synonym helpers ────────────────────────────────────────────────────────

    def normalise_skill(self, skill: str) -> str:
        return _apply_synonyms(skill, self._synonym_map)

    def normalise_skills(self, skills: list[str]) -> list[str]:
        return [self.normalise_skill(s) for s in skills]


# ── 3a + 3b  Skill matching & semantic similarity ─────────────────────────────

def _skill_overlap(candidate_skills: set[str], job_skills: list[str]) -> float:
    """
    Fraction of job_skills found in candidate_skills after synonym normalisation.
    Returns 1.0 when job_skills is empty (treat absent tier as fully satisfied).
    """
    if not job_skills:
        return 1.0
    job_set = set(job_skills)
    matched = len(candidate_skills & job_set)
    return matched / len(job_set)


def _compute_skill_features(
    resume: Resume,
    job: JobRequirement,
    engine: EmbeddingEngine,
) -> dict[str, float]:
    """
    Produces 5 features:
      mandatory_skill_overlap
      preferred_skill_overlap
      bonus_skill_overlap
      skill_coverage_score        — weighted blend of the three tier overlaps
      skill_semantic_similarity   — cosine sim between embedded skill lists
    """
    # Normalise through synonym map so "ml" == "machine learning" etc.
    candidate_skills = set(engine.normalise_skills(resume.skills))
    mandatory_skills = engine.normalise_skills(job.mandatory_skills)
    preferred_skills = engine.normalise_skills(job.preferred_skills)
    bonus_skills     = engine.normalise_skills(job.bonus_skills)

    mandatory_overlap = _skill_overlap(candidate_skills, mandatory_skills)
    preferred_overlap = _skill_overlap(candidate_skills, preferred_skills)
    bonus_overlap     = _skill_overlap(candidate_skills, bonus_skills)

    sw = skill_weights
    skill_coverage = (
        sw.mandatory  * mandatory_overlap
        + sw.preferred * preferred_overlap
        + sw.bonus     * bonus_overlap
    )

    # 3b — semantic similarity: resume skills vs all job skill tiers combined
    all_job_skills = mandatory_skills + preferred_skills + bonus_skills
    # Fallback: if JD has no skills at all, similarity is undefined → neutral 0.5
    if all_job_skills:
        skill_semantic = engine.mean_pool_sim(list(candidate_skills), all_job_skills)
    else:
        skill_semantic = 0.5

    return {
        "mandatory_skill_overlap":   round(mandatory_overlap, 6),
        "preferred_skill_overlap":   round(preferred_overlap, 6),
        "bonus_skill_overlap":       round(bonus_overlap,     6),
        "skill_coverage_score":      round(skill_coverage,    6),
        "skill_semantic_similarity": round(skill_semantic,    6),
    }


# ── 3c  Experience scoring ─────────────────────────────────────────────────────

def _compute_experience_features(
    resume: Resume,
    job: JobRequirement,
    engine: EmbeddingEngine,
) -> dict[str, float]:
    """
    Produces 3 features:
      meets_min_experience   — 1.0 if ≥ min; partial credit below (avoids cliff)
      experience_ratio       — candidate_yrs / preferred_yrs, capped at 1.0
      work_relevance_score   — embedding similarity of work descriptions to JD responsibilities
    """
    candidate_yrs = resume.total_years_experience
    min_yrs       = job.min_years_experience
    preferred_yrs = job.preferred_years_experience

    # Partial credit below minimum (soft floor)
    if min_yrs == 0:
        meets_min = 1.0
    elif candidate_yrs >= min_yrs:
        meets_min = 1.0
    else:
        meets_min = round(candidate_yrs / min_yrs, 6)

    # Ratio toward preferred years
    if preferred_yrs == 0:
        exp_ratio = 1.0
    else:
        exp_ratio = round(min(candidate_yrs / preferred_yrs, 1.0), 6)

    # Work-description relevance vs JD responsibilities
    work_texts        = [w.description for w in resume.work_experience]
    resp_texts        = job.responsibilities if job.responsibilities else [job.description]
    work_relevance    = engine.mean_pool_sim(work_texts, resp_texts)

    return {
        "meets_min_experience": meets_min,
        "experience_ratio":     exp_ratio,
        "work_relevance_score": round(work_relevance, 6),
    }


# ── 3d  Education scoring ──────────────────────────────────────────────────────

def _degree_score(candidate: DegreeLevel, required: DegreeLevel) -> float:
    """
    Ordinal ratio capped at 1.0.
    Overqualified (PhD for Bachelors role) → 1.0, never penalised.
    Underqualified → partial credit proportional to the gap.
    """
    if required.value == 0:
        return 1.0
    return round(min(candidate.value / required.value, 1.0), 6)


def _field_match_score(
    candidate_edu: Education,
    preferred_fields: list[str],
    engine: EmbeddingEngine,
) -> float:
    """
    Max cosine similarity between candidate's field_of_study and any preferred field.
    Returns 1.0 when no preferences are specified (not penalised for an open role).
    """
    if not preferred_fields:
        return 1.0
    candidate_emb      = engine.embed(candidate_edu.field_of_study)
    preferred_embs     = engine.embed_batch(preferred_fields)
    similarities       = [engine.cosine_sim(candidate_emb, pf) for pf in preferred_embs]
    return round(max(similarities), 6)


def _cgpa_score(edu: Education) -> float:
    """
    Normalise CGPA to [0.0, 1.0] on a 10-point scale.
    Returns neutral 0.5 when CGPA is absent.
    """
    if edu.cgpa is None:
        return 0.5
    return round(edu.cgpa / 10.0, 6)


def _compute_education_features(
    resume: Resume,
    job: JobRequirement,
    engine: EmbeddingEngine,
) -> dict[str, float]:
    """
    Produces 3 features:
      degree_level_score   — ordinal degree comparison
      field_match_score    — semantic match to preferred fields
      cgpa_score           — normalised CGPA
    """
    best_edu = resume.highest_degree
    return {
        "degree_level_score": _degree_score(best_edu.degree_level, job.required_degree),
        "field_match_score":  _field_match_score(best_edu, job.preferred_fields_of_study, engine),
        "cgpa_score":         _cgpa_score(best_edu),
    }


# ── 3e  Semantic JD matching ───────────────────────────────────────────────────

def _compute_jd_semantic_features(
    resume: Resume,
    job: JobRequirement,
    engine: EmbeddingEngine,
) -> dict[str, float]:
    """
    Produces 3 features:
      summary_jd_similarity      — professional_summary vs full JD text
      experience_jd_similarity   — combined work descriptions vs full JD text
      skill_jd_similarity        — skill list text vs JD responsibilities
    """
    jd_emb  = engine.embed(job.description)

    resp_text = (
        " ".join(job.responsibilities) if job.responsibilities else job.description
    )
    resp_emb  = engine.embed(resp_text)

    summary_emb   = engine.embed(resume.professional_summary)
    work_emb      = engine.embed(resume.combined_work_text)
    skills_emb    = engine.embed(" ".join(resume.skills))

    return {
        "summary_jd_similarity":    round(engine.cosine_sim(summary_emb, jd_emb),   6),
        "experience_jd_similarity": round(engine.cosine_sim(work_emb,    jd_emb),   6),
        "skill_jd_similarity":      round(engine.cosine_sim(skills_emb,  resp_emb), 6),
    }


# ── Aggregate signals ──────────────────────────────────────────────────────────

def _compute_aggregates(features: dict[str, float]) -> dict[str, float]:
    """
    overall_skill_score    — 60% keyword coverage + 40% semantic similarity
    overall_semantic_score — mean of the three JD-level semantic similarities
    """
    overall_skill = (
        0.60 * features["skill_coverage_score"]
        + 0.40 * features["skill_semantic_similarity"]
    )
    overall_semantic = float(np.mean([
        features["summary_jd_similarity"],
        features["experience_jd_similarity"],
        features["skill_jd_similarity"],
    ]))
    return {
        "overall_skill_score":    round(float(overall_skill),    6),
        "overall_semantic_score": round(float(overall_semantic), 6),
    }


# ── Public entry point ─────────────────────────────────────────────────────────

def extract_features(
    resume: Resume,
    job: JobRequirement,
    engine: EmbeddingEngine,
) -> FeatureVector:
    """
    Full feature extraction pipeline.

    Runs all five sub-pipelines and assembles a validated FeatureVector
    ready to be fed directly into the XGBoost model.

    Parameters
    ----------
    resume  : validated Resume object
    job     : validated JobRequirement object
    engine  : EmbeddingEngine (loaded once at startup, shared across calls)

    Returns
    -------
    FeatureVector with all 16 fields populated and validated in [0.0, 1.0].
    """
    logger.debug(
        "Extracting features — candidate=%s  job=%s",
        resume.candidate_id, job.job_id,
    )

    skill_feats      = _compute_skill_features(resume, job, engine)
    experience_feats = _compute_experience_features(resume, job, engine)
    education_feats  = _compute_education_features(resume, job, engine)
    jd_feats         = _compute_jd_semantic_features(resume, job, engine)

    all_feats  = {**skill_feats, **experience_feats, **education_feats, **jd_feats}
    aggregates = _compute_aggregates(all_feats)
    all_feats.update(aggregates)

    return FeatureVector(**all_feats)


# ── Component score helpers (consumed by scorer.py for ScoreBreakdown) ─────────

def component_scores(fv: FeatureVector) -> dict[str, float]:
    """
    Derive the four high-level component scores from a FeatureVector.
    These map directly to ScoreBreakdown and the training label formula.

      skill      = overall_skill_score
      experience = mean(meets_min, experience_ratio, work_relevance)
      education  = mean(degree_level, field_match, cgpa)
      semantic   = overall_semantic_score
    """
    return {
        "skill":      round(fv.overall_skill_score, 6),
        "experience": round(float(np.mean([
            fv.meets_min_experience,
            fv.experience_ratio,
            fv.work_relevance_score,
        ])), 6),
        "education":  round(float(np.mean([
            fv.degree_level_score,
            fv.field_match_score,
            fv.cgpa_score,
        ])), 6),
        "semantic":   round(fv.overall_semantic_score, 6),
    }