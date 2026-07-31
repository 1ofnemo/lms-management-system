import { useEffect, useState } from "react";
import api from "../api";

const STATUS_BADGE = {
  graded: "bg-success",
  needs_manual_review: "bg-warning text-dark",
  pending: "bg-secondary",
};

function Submissions() {
  const [submissions, setSubmissions] = useState([]);
  const [studentFilter, setStudentFilter] = useState("");
  const [assignmentFilter, setAssignmentFilter] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [score, setScore] = useState(0);
  const [strengths, setStrengths] = useState("");
  const [gaps, setGaps] = useState("");
  const [nextStep, setNextStep] = useState("");

  function loadData() {
    api.get("/submissions").then((res) => setSubmissions(res.data));
  }

  useEffect(loadData, []);

  const students = [
    ...new Map(submissions.map((s) => [s.student_id, s.student_name])).entries(),
  ].sort((a, b) => a[1].localeCompare(b[1]));

  const assignments = [
    ...new Map(submissions.map((s) => [s.assignment_id, s.assignment_prompt])).entries(),
  ];

  const filteredSubmissions = submissions.filter(
    (s) =>
      (!studentFilter || s.student_id === Number(studentFilter)) &&
      (!assignmentFilter || s.assignment_id === Number(assignmentFilter)),
  );

  function openEditModal(submission) {
    setEditing(submission);
    setScore(submission.score ?? 0);
    setStrengths((submission.feedback?.strengths ?? []).join("\n"));
    setGaps((submission.feedback?.gaps ?? []).join("\n"));
    setNextStep(submission.feedback?.next_step ?? "");
    setShowModal(true);
  }

  async function handleSave() {
    const feedback = {
      criterion_scores: editing.feedback?.criterion_scores ?? [],
      total: score,
      strengths: strengths.split("\n").filter((s) => s.trim() !== ""),
      gaps: gaps.split("\n").filter((g) => g.trim() !== ""),
      next_step: nextStep,
    };
    await api.patch(`/submissions/${editing.id}`, { score, feedback });
    setShowModal(false);
    loadData();
  }

  return (
    <div className="container py-4">
      <h1 className="h4 mb-3">Submissions</h1>

      <div className="row g-2 mb-3">
        <div className="col-sm-4">
          <select
            className="form-select"
            value={studentFilter}
            onChange={(e) => setStudentFilter(e.target.value)}
          >
            <option value="">All students</option>
            {students.map(([id, name]) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <div className="col-sm-6">
          <select
            className="form-select"
            value={assignmentFilter}
            onChange={(e) => setAssignmentFilter(e.target.value)}
          >
            <option value="">All assignments</option>
            {assignments.map(([id, prompt]) => (
              <option key={id} value={id}>
                {prompt.slice(0, 60)}
                {prompt.length > 60 ? "…" : ""}
              </option>
            ))}
          </select>
        </div>
        <div className="col-sm-2 d-flex align-items-center text-muted small">
          {filteredSubmissions.length} of {submissions.length}
        </div>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Student</th>
            <th>Assignment</th>
            <th>Status</th>
            <th>Score</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {filteredSubmissions.map((s) => (
            <tr key={s.id}>
              <td>{s.student_name}</td>
              <td>
                {s.assignment_prompt.slice(0, 60)}
                {s.assignment_prompt.length > 60 ? "…" : ""}
              </td>
              <td>
                <span className={`badge ${STATUS_BADGE[s.status] ?? "bg-secondary"}`}>
                  {s.status}
                </span>
              </td>
              <td>{s.score ?? "—"}</td>
              <td>
                <button
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => openEditModal(s)}
                >
                  Override
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && (
        <>
          <div className="modal d-block" tabIndex="-1">
            <div className="modal-dialog modal-lg">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    Override — {editing.student_name}
                  </h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowModal(false)}
                  />
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Answer</label>
                    <p className="text-muted">{editing.answer}</p>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Score</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      className="form-control"
                      value={score}
                      onChange={(e) => setScore(Number(e.target.value))}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Strengths (one per line)</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      value={strengths}
                      onChange={(e) => setStrengths(e.target.value)}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Gaps (one per line)</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      value={gaps}
                      onChange={(e) => setGaps(e.target.value)}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Next step</label>
                    <input
                      className="form-control"
                      value={nextStep}
                      onChange={(e) => setNextStep(e.target.value)}
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowModal(false)}
                  >
                    Cancel
                  </button>
                  <button className="btn btn-primary" onClick={handleSave}>
                    Save
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

export default Submissions;