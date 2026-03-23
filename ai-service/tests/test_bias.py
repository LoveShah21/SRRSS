from app.nlp.bias import detect_biased_terms


def test_detect_bias_flags_words():
    result = detect_biased_terms("We need a rockstar engineer and digital native")
    assert "rockstar" in result
    assert "digital native" in result
