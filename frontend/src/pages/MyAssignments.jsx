import { useEffect, useState } from "react";
import api from "../api";

function MyAssignments() {
  const [assignments, setAssignments] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [answer, setAnswer] = useState("");
  const [file, setFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/assignments").then((res) => setAssignments(res.data));
  }, []);

  function handleFileChange(e) {
    setFile(e.target.files[0] ?? null);
    setAnswer("");
  }

  async function handleSubmit() {
    setError("");
    setResult(null);
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("assignment_id", selectedId);
      if (file) {
        formData.append("file", file);
      } else {
        formData.append("answer", answer);
      }
      const res = await api.post("/submissions", formData);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail ?? "Submission failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container py-4">
      <h1 className="h4 mb-3">My Assignments</h1>

      <div className="mb-3">
        <label className="form-label">Assignment</label>
        <select
          className="form-select"
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
        >
          <option value="">Select an assignment…</option>
          {assignments.map((a) => (
            <option key={a.id} value={a.id}>
              {a.prompt.slice(0, 60)}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-3">
        <label className="form-label">Type your answer</label>
        <textarea
          className="form-control"
          rows="6"
          value={answer}
          disabled={!!file}
          onChange={(e) => setAnswer(e.target.value)}
        />
      </div>

      <div className="mb-3">
        <label className="form-label">…or upload a file (PDF or .docx)</label>
        <input
          type="file"
          className="form-control"
          accept=".pdf,.docx"
          onChange={handleFileChange}
        />
      </div>

      <button
        className="btn btn-primary"
        disabled={!selectedId || (!answer && !file) || submitting}
        onClick={handleSubmit}
      >
        {submitting ? "Grading…" : "Submit"}
      </button>

      {error && <div className="alert alert-danger mt-3">{error}</div>}

      {result && (
        <div className="card mt-4">
          <div className="card-body">
            {result.status === "needs_manual_review" ? (
              <p className="mb-0">
                Your submission is pending manual review by your teacher.
              </p>
            ) : (
              <>
                <h5 className="card-title">Score: {result.score}</h5>
                <table className="table table-sm">
                  <thead>
                    <tr>
                      <th>Criterion</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.feedback.criterion_scores.map((c, i) => (
                      <tr key={i}>
                        <td>{c.criterion}</td>
                        <td>{c.score}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p>
                  <strong>Strengths</strong>
                </p>
                <ul>
                  {result.feedback.strengths.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
                <p>
                  <strong>Gaps</strong>
                </p>
                <ul>
                  {result.feedback.gaps.map((g, i) => (
                    <li key={i}>{g}</li>
                  ))}
                </ul>
                <p>
                  <strong>Next step:</strong> {result.feedback.next_step}
                </p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default MyAssignments;
