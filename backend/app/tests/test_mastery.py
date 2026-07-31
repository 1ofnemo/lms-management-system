from app import mastery


def test_bucker_for_score_boundaries():
    assert mastery.bucker_for_score(0.85) == "advanced"
    assert mastery.bucker_for_score(0.84) == "average"
    assert mastery.bucker_for_score(0.6) == "average"
    assert mastery.bucker_for_score(0.59) == "struggling"


def test_trend_for_recent_needs_at_least_two_scores():
    assert mastery.trend_for_recent([]) == "flat"
    assert mastery.trend_for_recent([0.9]) == "flat"


def test_trend_for_recent_rising():
    assert mastery.trend_for_recent([0.9, 0.6]) == "rising"


def test_trend_for_recent_falling():
    assert mastery.trend_for_recent([0.6, 0.9]) == "falling"


def test_trend_for_recent_flat_within_deadband():
    assert mastery.trend_for_recent([0.72, 0.7]) == "flat"
