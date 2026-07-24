Mastery modal score grading notes for sprint 3 and 4:
Build it now — the retrofit cost later is small. The only piece of Sprint 4 that actually depends on Sprint 3 is the "recompute mastery on graded submission" trigger; the table itself, the bucketing function, and GET /progress don't need real submissions to exist, just rows in mastery_scores. And the backlog's own Sprint 6 explicitly endorses seeding that data directly rather than deriving it from live grading, so building it now with hand-seeded rows isn't cutting a corner — it's the intended demo path.

The tradeoff: when Sprint 3's grading pipeline eventually lands, you'll add one small call inside the grading endpoint (bucket_for_score() + upsert into mastery_scores) rather than getting that wiring "for free" as part of a single Sprint 3→4 pass. That's a trivial addition, not a redesign — worth it for having the Class Overview grid actually demoable today instead of blocked on an entire other sprint.

Two gaps I'm filling in that aren't literally spelled out in the backlog: (1) a GET /progress (no id, teacher/admin-only) endpoint that returns all students at once, since the backlog only defines the single-student GET /progress/{student_id}; (2) trend is scoped out entirely for this build — mastery_scores only stores a current value, not history, and the grid only needs bucket for the badge color anyway.

Use case notes:
MCQ needs a different UI and logic for testing
Need to populate class overview more properly
