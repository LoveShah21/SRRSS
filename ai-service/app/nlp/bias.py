BIAS_DICTIONARY = [
    "rockstar",
    "ninja",
    "aggressive",
    "dominant",
    "fearless",
    "young",
    "digital native",
]


def detect_biased_terms(job_description: str) -> list[str]:
    lowered = (job_description or "").lower()
    return [word for word in BIAS_DICTIONARY if word in lowered]
