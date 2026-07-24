def bucker_for_score(score: float) -> str:
    if score >= 0.85:
        return "advanced"
    if score >= 0.6:
        return "average"
    return "struggling"