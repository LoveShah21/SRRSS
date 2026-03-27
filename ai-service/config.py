"""
Central configuration — single source of truth for all tunable parameters.
Edit weights, thresholds, model paths, and grade bands here.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


# ── Project root ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent


class ScoringWeights(BaseSettings):
    """
    Weights used both during training label generation (Phase 4)
    and during inference (Phase 6).  Must sum to 1.0.
    """
    skill:      float = Field(default=0.40, ge=0.0, le=1.0)
    experience: float = Field(default=0.30, ge=0.0, le=1.0)
    education:  float = Field(default=0.15, ge=0.0, le=1.0)
    semantic:   float = Field(default=0.15, ge=0.0, le=1.0)

    model_config = {"env_prefix": "WEIGHT_"}

    def validate_sum(self) -> None:
        total = self.skill + self.experience + self.education + self.semantic
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {total:.4f}")


class SkillWeights(BaseSettings):
    """
    Sub-weights within the skill scoring component.
    Controls how mandatory / preferred / bonus tiers contribute.
    """
    mandatory:  float = Field(default=0.60, ge=0.0, le=1.0)
    preferred:  float = Field(default=0.30, ge=0.0, le=1.0)
    bonus:      float = Field(default=0.10, ge=0.0, le=1.0)

    model_config = {"env_prefix": "SKILL_"}


class ModelPaths(BaseSettings):
    """File paths for serialized artifacts produced by ml/train.py."""
    model_file:   Path = Field(default=BASE_DIR / "ml" / "artifacts" / "model.joblib")
    pipeline_file: Path = Field(default=BASE_DIR / "ml" / "artifacts" / "pipeline.joblib")
    synonyms_file: Path = Field(default=BASE_DIR / "ml" / "artifacts" / "synonyms.json")

    model_config = {"env_prefix": "MODEL_"}


class EmbeddingConfig(BaseSettings):
    """Controls the sentence-transformer embedding model."""
    model_name: str = Field(default="all-MiniLM-L6-v2")
    batch_size: int = Field(default=32, ge=1)
    device:     str = Field(default="cpu")        # "cuda" if GPU available

    model_config = {"env_prefix": "EMBED_"}


class TrainingConfig(BaseSettings):
    """Synthetic data generation + XGBoost training hyper-parameters."""
    n_samples:       int   = Field(default=2000,  ge=100)
    test_split:      float = Field(default=0.20,  ge=0.05, le=0.40)
    random_seed:     int   = Field(default=42)

    # XGBoost
    n_estimators:    int   = Field(default=300,   ge=10)
    max_depth:       int   = Field(default=4,     ge=1,  le=10)
    learning_rate:   float = Field(default=0.05,  ge=0.001, le=1.0)
    subsample:       float = Field(default=0.8,   ge=0.1, le=1.0)
    colsample_bytree: float = Field(default=0.8,  ge=0.1, le=1.0)

    model_config = {"env_prefix": "TRAIN_"}


class GradeBands(BaseSettings):
    """
    Score → grade mapping.  Scores are in [0.0, 1.0].
    Thresholds are inclusive lower bounds.
    """
    a_plus:  float = Field(default=0.90)
    a:       float = Field(default=0.80)
    b_plus:  float = Field(default=0.70)
    b:       float = Field(default=0.60)
    c:       float = Field(default=0.50)
    # Below 0.50 → D (not a fit)

    model_config = {"env_prefix": "GRADE_"}

    def score_to_grade(self, score: float) -> str:
        if score >= self.a_plus:  return "A+"
        if score >= self.a:       return "A"
        if score >= self.b_plus:  return "B+"
        if score >= self.b:       return "B"
        if score >= self.c:       return "C"
        return "D"


class RankingConfig(BaseSettings):
    """Controls batch ranking behaviour (Phase 7)."""
    default_top_n:      int   = Field(default=10,  ge=1)
    min_score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)

    model_config = {"env_prefix": "RANK_"}


class APIConfig(BaseSettings):
    """FastAPI server settings."""
    host:    str = Field(default="0.0.0.0")
    port:    int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1,    ge=1)
    title:   str = Field(default="Resume Scorer API")
    version: str = Field(default="1.0.0")

    model_config = {"env_prefix": "API_"}


# ── Singleton instances (import these everywhere) ────────────────────────────
scoring_weights  = ScoringWeights()
skill_weights    = SkillWeights()
model_paths      = ModelPaths()
embedding_config = EmbeddingConfig()
training_config  = TrainingConfig()
grade_bands      = GradeBands()
ranking_config   = RankingConfig()
api_config       = APIConfig()