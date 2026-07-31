import { useEffect, useState } from "react";
import api from "../api";

function ManageAssignments() {
  const [assignments, setAssignments] = useState([]);
  const [topics, setTopics] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [criteria, setCriteria] = useState([{ criterion: "", weight: 0 }]);
  const [options, setOptions] = useState(["", ""]);
  const [correctAnswer, setCorrectAnswer] = useState("");

  const [editingAssignment, setEditingAssignment] = useState(null);
  const [topicId, setTopicId] = useState("");
  const [type, setType] = useState("essay");
  const [prompt, setPrompt] = useState("");

  function loadData() {
    api.get("/assignments").then((res) => setAssignments(res.data));
    api.get("/topics").then((res) => setTopics(res.data));
  }

  useEffect(loadData, []);

  function updateCriterion(index, field, value) {
    setCriteria(
      criteria.map((row, i) =>
        i === index ? { ...row, [field]: value } : row,
      ),
    );
  }

  function addCriterionRow() {
    setCriteria([...criteria, { criterion: "", weight: 0 }]);
  }

  function removeCriterionRow(index) {
    setCriteria(criteria.filter((_, i) => i !== index));
  }

  function updateOption(index, value) {
    setOptions(options.map((o, i) => (i === index ? value : o)));
  }

  function addOptionRow() {
    setOptions([...options, ""]);
  }

  function removeOptionRow(index) {
    setOptions(options.filter((_, i) => i !== index));
  }

  function openCreateModal() {
    setEditingAssignment(null);
    setTopicId("");
    setType("essay");
    setPrompt("");
    setCriteria([{ criterion: "", weight: 0 }]);
    setOptions(["", ""]);
    setCorrectAnswer("");
    setShowModal(true);
  }

  function openEditModal(a) {
    setEditingAssignment(a);
    setTopicId(a.topic_id);
    setType(a.type);
    setPrompt(a.prompt);
    setCriteria(a.rubric.criteria ?? [{ criterion: "", weight: 0 }]);
    setOptions(a.rubric.options ?? ["", ""]);
    setCorrectAnswer(a.rubric.correct_answer ?? "");
    setShowModal(true);
  }

  async function handleSubmit() {
    const rubric =
      type === "mcq" ? { options, correct_answer: correctAnswer } : { criteria };
    const body = { topic_id: topicId, type, prompt, rubric };
    if (editingAssignment) {
      await api.put(`/assignments/${editingAssignment.id}`, body);
    } else {
      await api.post("/assignments", body);
    }
    setShowModal(false);
    loadData();
  }

  async function handleDelete(id) {
    await api.delete(`/assignments/${id}`);
    loadData();
  }

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1 className="h4 mb-0">Manage Assignments</h1>
        <button className="btn btn-primary" onClick={openCreateModal}>
          Add Assignment
        </button>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Topic</th>
            <th>Type</th>
            <th>Prompt</th>
            <th>Rubric</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {assignments.map((a) => (
            <tr key={a.id}>
              <td>
                {topics.find((t) => t.id === a.topic_id)?.name ?? a.topic_id}
              </td>
              <td>{a.type}</td>
              <td>
                {a.prompt.slice(0, 60)}
                {a.prompt.length > 60 ? "…" : ""}
              </td>
              <td>
                {a.type === "mcq"
                  ? a.rubric.options
                      ?.map(
                        (o) =>
                          `${o}${o === a.rubric.correct_answer ? " ✓" : ""}`,
                      )
                      .join(", ")
                  : a.rubric.criteria
                      ?.map((c) => `${c.criterion} (${c.weight})`)
                      .join(", ")}
              </td>
              <td>
                <button
                  className="btn btn-sm btn-outline-secondary me-2"
                  onClick={() => openEditModal(a)}
                >
                  Edit
                </button>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => handleDelete(a.id)}
                >
                  Delete
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
                    {editingAssignment ? "Edit Assignment" : "New Assignment"}
                  </h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowModal(false)}
                  />
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Topic</label>
                    <select
                      className="form-select"
                      value={topicId}
                      onChange={(e) => setTopicId(Number(e.target.value))}
                    >
                      <option value="">Select a topic…</option>
                      {topics.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Type</label>
                    <select
                      className="form-select"
                      value={type}
                      onChange={(e) => setType(e.target.value)}
                    >
                      <option value="essay">Essay</option>
                      <option value="mcq">MCQ</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Prompt</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                    />
                  </div>
                  {type === "essay" && (
                    <div className="mb-3">
                      <label className="form-label">Rubric</label>
                      {criteria.map((row, i) => (
                        <div className="d-flex gap-2 mb-2" key={i}>
                          <input
                            className="form-control"
                            placeholder="Criterion"
                            value={row.criterion}
                            onChange={(e) =>
                              updateCriterion(i, "criterion", e.target.value)
                            }
                          />
                          <input
                            type="number"
                            step="0.1"
                            className="form-control"
                            style={{ maxWidth: 100 }}
                            placeholder="Weight"
                            value={row.weight}
                            onChange={(e) =>
                              updateCriterion(
                                i,
                                "weight",
                                Number(e.target.value),
                              )
                            }
                          />
                          <button
                            type="button"
                            className="btn btn-outline-danger"
                            onClick={() => removeCriterionRow(i)}
                            disabled={criteria.length === 1}
                          >
                            &times;
                          </button>
                        </div>
                      ))}
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary"
                        onClick={addCriterionRow}
                      >
                        + Add Criterion
                      </button>
                    </div>
                  )}

                  {type === "mcq" && (
                    <div className="mb-3">
                      <label className="form-label">
                        Options (select the correct one)
                      </label>
                      {options.map((opt, i) => (
                        <div
                          className="d-flex gap-2 mb-2 align-items-center"
                          key={i}
                        >
                          <input
                            type="radio"
                            name="correctAnswer"
                            checked={correctAnswer === opt && opt !== ""}
                            onChange={() => setCorrectAnswer(opt)}
                          />
                          <input
                            className="form-control"
                            placeholder={`Option ${i + 1}`}
                            value={opt}
                            onChange={(e) => updateOption(i, e.target.value)}
                          />
                          <button
                            type="button"
                            className="btn btn-outline-danger"
                            onClick={() => removeOptionRow(i)}
                            disabled={options.length === 2}
                          >
                            &times;
                          </button>
                        </div>
                      ))}
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary"
                        onClick={addOptionRow}
                      >
                        + Add Option
                      </button>
                    </div>
                  )}
                </div>
                <div className="modal-footer">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowModal(false)}
                  >
                    Cancel
                  </button>
                  <button className="btn btn-primary" onClick={handleSubmit}>
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

export default ManageAssignments;
