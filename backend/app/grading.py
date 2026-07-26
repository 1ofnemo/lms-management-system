import anthropic
import json
import logging

from app.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5"

GRADING_SCHEMA = {
    "type": "object",
    "properties": {
        "criterion_scores": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "criterion": {"type": "string"},
                    "score": {"type": "number"}
                },
                "required": ["criterion", "score"],
                "additionalProperties": False,
            },
        },
        "total": {"type": "number"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
    },
    "required": ["criterion_scores", "total", "strengths", "gaps", "next_step"],
    "additionalProperties": False,
}

# Sample JSON output (for my own reference):
# {
#   "criterion_scores": [
#     { "criterion": "Thesis clarity", "score": 0.8 },
#     { "criterion": "Evidence use", "score": 0.6 }
#   ],
#   "total": 0.7,
#   "strengths": [
#     "Clear thesis stated in the opening sentence",
#     "Uses two relevant examples"
#   ],
#   "gaps": [
#     "Evidence isn't tied back to the thesis explicitly"
#   ],
#   "next_step": "Add a sentence after each example explaining how it supports your thesis."
# }


def build_grading_prompt(prompt: str, rubric: dict, answer: str) -> str:
    criteria_lines = "\n".join(
        f"- {c['criterion']} (weight: {c['weight']})" for c in rubric["criteria"]
    )

    return (
        f"Assignment prompt:\n{prompt}\n\n"
        f"Rubric criteria:\n{criteria_lines}\n\n"
        f"Student answer:\n{answer}\n\n"
        "Grade the answer against every criterion above. Score each criterion "
        "0.0-1.0, compute a weighted total, and give concrete strengths, gaps, "
        "and a single next step for the student."
    )


def grade_submission (assignment_prompt: str, rubric: dict, answer: str) -> dict: 
    message_prompt = build_grading_prompt(assignment_prompt, rubric, answer)
    response = client.messages.create(
        model = MODEL,
        max_tokens=1024,
        output_config={"format": {"type": "json_schema", "schema": GRADING_SCHEMA}},
        messages=[{"role": "user", "content": message_prompt}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def grade_submission_with_retry(assignment_prompt: str, rubric: dict, answer: str) -> dict | None:
    for attempt in range(2):
        try:
            return grade_submission(assignment_prompt, rubric, answer)
        except (anthropic.APIError, json.JSONDecodeError) as e:
            logger.warning("Grading attempt %d failed: %s", attempt + 1, e)
    return None

