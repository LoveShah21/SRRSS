import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


def _token_overlap_score(job_description: str, candidate_resume_text: str) -> float:
    job_tokens = set(re.findall(r"[a-zA-Z0-9.+#]+", (job_description or "").lower()))
    candidate_tokens = set(re.findall(r"[a-zA-Z0-9.+#]+", (candidate_resume_text or "").lower()))
    if not job_tokens:
        return 0.0
    overlap = len(job_tokens.intersection(candidate_tokens))
    return round((overlap / len(job_tokens)) * 100, 2)

def calculate_match_score(job_description: str, candidate_resume_text: str) -> float:
    """
    Calculates semantic match using TF-IDF and Cosine Similarity.
    """
    if SKLEARN_AVAILABLE:
        documents = [job_description, candidate_resume_text]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = similarity[0][0] * 100
        return round(score, 2)

    return _token_overlap_score(job_description, candidate_resume_text)
