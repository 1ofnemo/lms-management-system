import anthropic

from app.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-haiku-4-5"


def build_analysis_prompt(student_name: str, topic_rows: list[dict], submissions: list[dict], recommendation_text: str) -> str:
    topic_lines = "\n".join(
        f"- {r['topic_name']}: {round(r['score'] * 100)}% ({r['bucket']}, trend: {r['trend']})"
        for r in topic_rows
    )

    submission_lines = []
    for s in submissions:
        line = f"- {s['topic_name']} ({s['assignment_type']}), {s['graded_at'].date()}: {round(s['score'] * 100)}%"
        feedback = s["feedback"] or {}
        strengths = feedback.get("strengths") or []
        gaps = feedback.get("gaps") or []
        if strengths:
            line += f" | strengths noted: {'; '.join(strengths)}"
        if gaps:
            line += f" | gaps noted: {'; '.join(gaps)}"
        submission_lines.append(line)
    submission_block = "\n".join(submission_lines)

    return (
        f"You're an academic advisor reviewing {student_name}'s progress in an algebra curriculum.\n\n"
        f"Topic-by-topic mastery so far:\n{topic_lines}\n\n"
        f"Full submission history, oldest to newest:\n{submission_block}\n\n"
        f"The system's current recommendation for what to work on next: {recommendation_text}\n\n"
        "Write a natural, honest, and encouraging analysis of this student's learning journey so far -- "
        "flowing prose, not a bulleted list or a rigid template, like a real teacher writing a personal "
        "note after reviewing a report card. Cover: an overall sense of how they're doing, specific "
        "strengths worth calling out (referencing the actual feedback above, not just restating scores), "
        "specific areas that need work, any trend worth mentioning, and a closing note connecting to what "
        "they should focus on next. Aim for roughly 300-500 words. Interpret the data and form a genuine "
        "impression -- don't just list the numbers back."
    )


def generate_analysis(student_name: str, topic_rows: list[dict], submissions: list[dict], recommendation_text: str) -> str:
    prompt = build_analysis_prompt(student_name, topic_rows, submissions, recommendation_text)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(b.text for b in response.content if b.type == "text")