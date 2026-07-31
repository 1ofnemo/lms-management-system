from app.models import MasteryScore, Topic
from app.roadmap import Recommendation, adjust_for_bucket, next_unlocked_topic, reason_message


def _topic(topic_id, prerequisite_ids=None):
    return Topic(id=topic_id, name=f"Topic {topic_id}", prerequisite_ids=prerequisite_ids or [])


def _mastery(topic_id, score, bucket):
    return MasteryScore(topic_id=topic_id, score=score, bucket=bucket)


# -- next_unlocked_topic --------------------------------------------------


def test_root_topic_is_next_for_a_fresh_student():
    topics = [_topic(1), _topic(2, [1])]
    assert next_unlocked_topic(topics, mastered_topic_ids=set()).id == 1


def test_child_topic_unlocks_once_its_prerequisite_is_mastered():
    topics = [_topic(1), _topic(2, [1])]
    assert next_unlocked_topic(topics, mastered_topic_ids={1}).id == 2


def test_mastered_topics_are_never_recommended():
    topics = [_topic(1)]
    assert next_unlocked_topic(topics, mastered_topic_ids={1}) is None


def test_topic_stays_locked_until_every_prerequisite_is_mastered():
    topics = [_topic(1), _topic(2), _topic(3, [1, 2])]
    assert next_unlocked_topic(topics, mastered_topic_ids={1}).id == 2  # 3 needs both 1 and 2


def test_branching_ties_are_broken_by_lowest_topic_id():
    # deliberately out of id order, to prove the function sorts internally
    topics = [_topic(1), _topic(3, [1]), _topic(2, [1])]
    assert next_unlocked_topic(topics, mastered_topic_ids={1}).id == 2


def test_dangling_prerequisite_reference_locks_a_topic_forever():
    # topic 99 doesn't exist in the topic list at all (e.g. deleted after this topic referenced it)
    topics = [_topic(2, [99])]
    assert next_unlocked_topic(topics, mastered_topic_ids=set()) is None


def test_no_topics_returns_none():
    assert next_unlocked_topic([], mastered_topic_ids=set()) is None


# -- adjust_for_bucket -----------------------------------------------------


def test_adjust_returns_complete_when_every_topic_is_mastered():
    topics = [_topic(1)]
    rec = adjust_for_bucket(None, trigger=None, topics=topics, mastered_topic_ids={1}, mastery_scores=[])
    assert rec == Recommendation(None, "complete", None)


def test_adjust_returns_stuck_when_topics_remain_but_none_are_unlocked():
    # topic 2's only prerequisite (99) doesn't exist, so it can never unlock
    topics = [_topic(2, [99])]
    rec = adjust_for_bucket(None, trigger=None, topics=topics, mastered_topic_ids=set(), mastery_scores=[])
    assert rec == Recommendation(None, "stuck", None)


def test_adjust_leaves_recommendation_unchanged_with_no_mastery_history():
    next_topic = _topic(2, [1])
    rec = adjust_for_bucket(
        next_topic, trigger=None, topics=[next_topic], mastered_topic_ids=set(), mastery_scores=[]
    )
    assert rec == Recommendation(next_topic, "on_track", None)


def test_adjust_leaves_recommendation_unchanged_for_average_bucket():
    next_topic = _topic(2, [1])
    trigger = _mastery(1, score=0.7, bucket="average")
    rec = adjust_for_bucket(
        next_topic, trigger, topics=[next_topic], mastered_topic_ids={1}, mastery_scores=[trigger]
    )
    assert rec == Recommendation(next_topic, "on_track", None)


def test_advanced_bucket_skips_ahead_and_names_the_trigger_topic():
    topics = [_topic(1), _topic(2, [1]), _topic(3, [2])]
    next_topic = topics[1]  # topic 2, already unlocked
    trigger = _mastery(1, score=0.9, bucket="advanced")  # topic 1 is what triggered this
    rec = adjust_for_bucket(
        next_topic, trigger, topics=topics, mastered_topic_ids={1}, mastery_scores=[trigger]
    )
    assert rec.topic.id == 3
    assert rec.reason == "skip_ahead"
    assert rec.context_topic.id == 1


def test_advanced_bucket_falls_back_when_next_topic_is_the_last_one():
    topics = [_topic(1), _topic(2, [1])]
    next_topic = topics[1]  # nothing comes after topic 2
    trigger = _mastery(1, score=0.9, bucket="advanced")
    rec = adjust_for_bucket(
        next_topic, trigger, topics=topics, mastered_topic_ids={1}, mastery_scores=[trigger]
    )
    assert rec == Recommendation(next_topic, "on_track", None)


def test_advanced_bucket_does_not_skip_past_a_struggling_next_topic():
    # trigger (topic 2) is advanced, but next_topic (topic 1) is itself a known struggle --
    # skipping past it would abandon a weak foundational topic just because something else looks good.
    topics = [_topic(1), _topic(2, [1]), _topic(3, [1])]
    next_topic = topics[0]  # topic 1: unlocked, unmastered, and struggling
    mastery_scores = [
        _mastery(1, score=0.33, bucket="struggling"),
        _mastery(2, score=0.9, bucket="advanced"),
    ]
    trigger = mastery_scores[1]
    rec = adjust_for_bucket(
        next_topic, trigger, topics=topics, mastered_topic_ids={2}, mastery_scores=mastery_scores
    )
    assert rec == Recommendation(next_topic, "on_track", None)


def test_struggling_bucket_inserts_the_weakest_off_path_topic():
    topics = [_topic(1), _topic(2, [1]), _topic(3, [1]), _topic(4, [1])]
    next_topic = topics[1]  # topic 2
    mastery_scores = [
        _mastery(3, score=0.5, bucket="struggling"),
        _mastery(4, score=0.3, bucket="struggling"),  # weaker than topic 3
    ]
    trigger = mastery_scores[-1]  # which row is "most recent" doesn't affect who's weakest
    rec = adjust_for_bucket(
        next_topic, trigger, topics=topics, mastered_topic_ids={1}, mastery_scores=mastery_scores
    )
    assert rec.topic.id == 4
    assert rec.reason == "remedial"
    assert rec.context_topic is next_topic  # what they're being diverted from


def test_struggling_bucket_ignores_the_recommended_topic_itself():
    topics = [_topic(1), _topic(2, [1])]
    next_topic = topics[1]  # topic 2
    mastery_scores = [_mastery(2, score=0.4, bucket="struggling")]  # only weak spot IS next_topic
    trigger = mastery_scores[0]
    rec = adjust_for_bucket(
        next_topic, trigger, topics=topics, mastered_topic_ids={1}, mastery_scores=mastery_scores
    )
    assert rec == Recommendation(next_topic, "on_track", None)


def test_struggling_bucket_falls_back_with_no_other_weak_topics():
    topics = [_topic(1), _topic(2, [1])]
    next_topic = topics[1]
    trigger = _mastery(1, score=0.28, bucket="struggling")
    rec = adjust_for_bucket(
        next_topic, trigger, topics=topics, mastered_topic_ids={1}, mastery_scores=[]
    )
    assert rec == Recommendation(next_topic, "on_track", None)


def test_struggling_bucket_does_not_redirect_when_next_topic_is_itself_the_weakest():
    # next_topic (1) is unlocked and unmastered, and also the WORST score overall --
    # redirecting to topic 2 (a merely-mediocre score) would be a worse recommendation.
    topics = [_topic(1), _topic(2, [1])]
    next_topic = topics[0]  # topic 1
    mastery_scores = [
        _mastery(1, score=0.28, bucket="struggling"),
        _mastery(2, score=0.31, bucket="struggling"),
    ]
    trigger = mastery_scores[0]
    rec = adjust_for_bucket(
        next_topic, trigger, topics=topics, mastered_topic_ids=set(), mastery_scores=mastery_scores
    )
    assert rec == Recommendation(next_topic, "on_track", None)


# -- reason_message ---------------------------------------------------------


def test_reason_message_on_track():
    rec = Recommendation(_topic(2), "on_track", None)
    assert reason_message(rec) == "This is the next topic in your learning path."


def test_reason_message_complete():
    rec = Recommendation(None, "complete", None)
    assert "mastered every topic" in reason_message(rec)


def test_reason_message_stuck():
    rec = Recommendation(None, "stuck", None)
    assert "check with your teacher" in reason_message(rec)


def test_reason_message_skip_ahead_names_the_trigger_topic():
    rec = Recommendation(_topic(3), "skip_ahead", context_topic=_topic(1))
    assert "Topic 1" in reason_message(rec)


def test_reason_message_remedial_names_the_deferred_topic():
    rec = Recommendation(_topic(4), "remedial", context_topic=_topic(2))
    assert "Topic 2" in reason_message(rec)