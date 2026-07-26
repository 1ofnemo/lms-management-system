# just an attempt at writing unit test for this repo build
# to ensure that grading prompt for Claude works & that the logic works

import json

from app import grading

def test_build_grading_prompt_including_every_criterion():
    rubric = {
        "criteria": [
            {"criterion": "Thesis clarity", "weight": 0.5},
            {"criterion": "Evidence use", "weight": 0.5},
        ]
    }
    prompt = grading.build_grading_prompt(
        "Explain photosynthesis.", rubric, "Plants use sunlight."
    )
    assert "Thesis clarity" in prompt
    assert "Evidence use" in prompt
    assert "Explain photosynthesis." in prompt
    assert "Plants use sunlight." in prompt

def test_grade_submission_with_retry_stops_after_two_failures(monkeypatch):
    calls = []

    def fake_grade_submission(*args, **kwargs):
        calls.append(1)
        raise json.JSONDecodeError("bad json", "", 0)
    
    monkeypatch.setattr(grading, "grade_submission", fake_grade_submission)

    result = grading.grade_submission_with_retry("prompt", {"criteria": []}, "answer")

    assert result is None
    assert len(calls) == 2


def test_grade_submission_with_retry_does_not_retry_on_success(monkeypatch):
    calls = []

    def fake_grade_submission(*args, **kwargs):
        calls.append(1)
        return {"total": 1.0}

    monkeypatch.setattr(grading, "grade_submission", fake_grade_submission)

    result = grading.grade_submission_with_retry("prompt", {"criteria": []}, "answer")

    assert result == {"total": 1.0}
    assert len(calls) == 1