import { useEffect, useState } from "react";
import api, { getCurrentUser } from "../api";
import { BUCKET_BADGE_CLASS, TREND_ICON } from "../masteryDisplay";
import TopicMap from "../components/TopicMap";
import AssignmentScoreChart from "../components/AssignmentScoreChart";
import InsightsPanel from "../components/InsightsPanel";
import ScoreTrendChart from "../components/ScoreTrendChart";

function Dashboard() {
  const user = getCurrentUser();
  const [rows, setRows] = useState([]);
  const [nextRecommendation, setNextRecommendation] = useState(null);
  const [topics, setTopics] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  async function handleAnalyze() {
    setShowAnalysis(true);
    setAnalysisLoading(true);
    setAnalysisError("");
    setAnalysis(null);
    try {
      const res = await api.post(`/progress/${user.id}/analysis`);
      setAnalysis(res.data.analysis);
    } catch {
      setAnalysisError("Couldn't generate your analysis right now. Please try again.");
    } finally {
      setAnalysisLoading(false);
    }
  }

  useEffect(() => {
    if (user?.role === "student") {
      api.get(`/progress/${user.id}`).then((res) => setRows(res.data));
      api.get(`/progress/${user.id}/next`).then((res) => setNextRecommendation(res.data));
      api.get("/topics").then((res) => setTopics(res.data));
      api.get(`/progress/${user.id}/submissions`).then((res) => setSubmissions(res.data));
    }
  }, [user?.id, user?.role]);

  return (
    <div className="container py-4">
      <h1 className="h4 mb-3">Dashboard</h1>
      <p>Logged in as {user?.role}.</p>

      {user?.role === "student" && nextRecommendation && (
        <div className="card mb-4 shadow-sm">
          <div className="card-body d-flex align-items-start gap-3">
            <div className="fs-2" aria-hidden="true">
              {nextRecommendation.topic ? "🎯" : "🎉"}
            </div>
            <div>
              <div className="text-uppercase text-muted small fw-semibold mb-1">
                Recommended Next
              </div>
              <h5 className="card-title mb-1">
                {nextRecommendation.topic ? nextRecommendation.topic.name : "You're all caught up!"}
              </h5>
              <p className="card-text text-muted mb-2">{nextRecommendation.reason}</p>
              <button className="btn btn-sm btn-outline-primary" onClick={handleAnalyze}>
                Analyze your Learning
              </button>
            </div>
          </div>
        </div>
      )}

      {user?.role === "student" && (
        <TopicMap
          topics={topics}
          progressRows={rows}
          nextTopicId={nextRecommendation?.topic?.id ?? null}
        />
      )}

      {user?.role === "student" && <InsightsPanel submissions={submissions} />}

      {user?.role === "student" && <AssignmentScoreChart submissions={submissions} />}

      {user?.role === "student" && rows.length > 0 && (
        <h2 className="h6 text-muted mb-3">Your Progress</h2>
      )}

      {user?.role === "student" &&
        (rows.length === 0 ? (
          <p className="text-muted">
            No progress yet — submit an assignment to get started.
          </p>
        ) : (
          rows.map((r) => {
            const pct = Math.round(r.score * 100);
            const trendData = submissions
              .filter((s) => s.topic_id === r.topic_id && s.score !== null)
              .map((s) => ({ date: s.graded_at.slice(0, 10), score: s.score }));

            return (
              <div className="mb-4" key={r.topic_id}>
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <span>{r.topic_name}</span>
                  <span className={`badge ${BUCKET_BADGE_CLASS[r.bucket]}`}>
                    {r.bucket}
                    {TREND_ICON[r.trend]}
                  </span>
                </div>
                <div
                  className="progress"
                  role="progressbar"
                  aria-valuenow={pct}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  <div
                    className={`progress-bar ${BUCKET_BADGE_CLASS[r.bucket]}`}
                    style={{ width: `${pct}%` }}
                  >
                    {pct}%
                  </div>
                </div>
                <ScoreTrendChart data={trendData} />
              </div>
            );
          })
        ))}

      {showAnalysis && (
        <>
          <div className="modal d-block" tabIndex="-1">
            <div className="modal-dialog modal-lg">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Your Learning Analysis</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowAnalysis(false)}
                  />
                </div>
                <div className="modal-body">
                  {analysisLoading && (
                    <div className="text-center py-4">
                      <div className="spinner-border text-primary" role="status" />
                      <p className="text-muted mt-2 mb-0">Analyzing your progress…</p>
                    </div>
                  )}
                  {analysisError && (
                    <div className="alert alert-danger mb-0">{analysisError}</div>
                  )}
                  {analysis && <p style={{ whiteSpace: "pre-wrap" }}>{analysis}</p>}
                </div>
                <div className="modal-footer">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowAnalysis(false)}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop show" />
        </>
      )}
    </div>
  );
}

export default Dashboard;