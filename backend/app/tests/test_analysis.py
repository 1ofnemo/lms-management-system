from datetime import datetime

from app import analysis


def test_build_analysis_prompt_includes_all_data():
    topic_rows = [
        {"topic_name": "Intro to Algebra", "score": 0.72, "bucket": "average", "trend": "rising"},
    ]
    submissions = [
        {
            "topic_name": "Intro to Algebra",
            "assignment_type": "essay",
            "score": 0.7,
            "graded_at": datetime(2026, 7, 1),
            "feedback": {"strengths": ["Clear reasoning"], "gaps": ["Missing final step"]},
        },
    ]

    prompt = analysis.build_analysis_prompt("Jane Doe", topic_rows, submissions, "Try Linear Equations next.")

    assert "Jane Doe" in prompt
    assert "Intro to Algebra" in prompt
    assert "72%" in prompt
    assert "average" in prompt
    assert "rising" in prompt
    assert "Clear reasoning" in prompt
    assert "Missing final step" in prompt
    assert "Try Linear Equations next." in prompt


def test_build_analysis_prompt_handles_submission_with_no_feedback():
    topic_rows = [{"topic_name": "Intro to Algebra", "score": 1.0, "bucket": "advanced", "trend": "flat"}]
    submissions = [
        {
            "topic_name": "Intro to Algebra",
            "assignment_type": "mcq",
            "score": 1.0,
            "graded_at": datetime(2026, 7, 1),
            "feedback": None,
        },
    ]

    prompt = analysis.build_analysis_prompt("Jane Doe", topic_rows, submissions, "Nothing left to recommend.")

    assert "Intro to Algebra" in prompt