from app.models.scorer import calculate_match_score


def test_calculate_match_score_range():
    job_text = "Looking for python developer with fastapi and mongodb experience"
    candidate_text = "Python developer experienced in FastAPI and MongoDB building APIs"

    score = calculate_match_score(job_text, candidate_text)

    assert 0 <= score <= 100
    assert score > 20
