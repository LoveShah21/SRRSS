import re

try:
    import spacy

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = spacy.blank("en")
except Exception:
    spacy = None
    nlp = None

def extract_entities(text: str):
    doc = nlp(text) if nlp else None
    entities = {"PERSON": [], "ORG": [], "SKILLS": [], "EMAIL": [], "EDUCATION": [], "EXPERIENCE": []}
    
    # Needs a dedicated skill dictionary or trained NER model for comprehensive extraction
    common_skills = [
        "python", "java", "sql", "react", "node.js", "machine learning",
        "docker", "aws", "fastapi", "flask", "express", "mongodb", "tailwind"
    ]
    
    if doc is not None:
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)

    email_matches = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    entities["EMAIL"] = sorted(set(email_matches))
            
    if doc is not None:
        for token in doc:
            if token.text.lower() in common_skills:
                if token.text.lower() not in entities["SKILLS"]:
                    entities["SKILLS"].append(token.text.lower())
    else:
        text_lower = text.lower()
        for skill in common_skills:
            if skill in text_lower:
                entities["SKILLS"].append(skill)

    lowered_lines = [line.strip() for line in text.splitlines() if line.strip()]
    education_markers = ["b.sc", "btech", "m.sc", "mba", "phd", "bachelor", "master", "university", "college"]
    experience_markers = ["engineer", "developer", "intern", "manager", "analyst", "consultant"]

    entities["EDUCATION"] = [
        line for line in lowered_lines if any(marker in line.lower() for marker in education_markers)
    ][:5]
    entities["EXPERIENCE"] = [
        line for line in lowered_lines if any(marker in line.lower() for marker in experience_markers)
    ][:8]
                
    return entities
