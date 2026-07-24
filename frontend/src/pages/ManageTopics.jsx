import { useEffect, useState } from "react";
import api from "../api";

function ManageTopics() {
  const [topics, setTopics] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingTopic, setEditingTopic] = useState(null); //null - creating
  const [name, setName] = useState("");
  const [prereqIds, setprereqIds] = useState([]);

  function loadTopics() {
    api.get("/topics").then((res) => setTopics(res.data));
  }

  useEffect(loadTopics, []);

  function openCreateModal() {
    setEditingTopic(null);
    setName("");
    setprereqIds([]);
    setShowModal(true);
  }

  function openEditModal(topic) {
    setEditingTopic(topic);
    setName(topic.name);
    setprereqIds(topic.prerequisite_ids);
    setShowModal(true);
  }

  async function handleSubmit() {
    const body = { name, prerequisite_ids: prereqIds };
    if (editingTopic) {
      await api.put(`/topics/${editingTopic.id}`, body);
    } else {
      await api.post("/topics", body);
    }
    setShowModal(false);
    loadTopics();
  }

  async function handleDelete(id) {
    await api.delete(`/topics/${id}`);
    loadTopics();
  }

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1 className="h4 mb-0">Manage Topics</h1>
        <button className="btn btn-primary" onClick={openCreateModal}>
          Add Topic
        </button>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Prerequisites</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {topics.map((t) => (
            <tr key={t.id}>
              <td>{t.name}</td>
              <td>
                {t.prerequisite_ids
                  .map((id) => topics.find((x) => x.id === id)?.name ?? id)
                  .join(", ")}
              </td>
              <td>
                <button className="btn btn-sm btn-outline-secondary me-2" onClick={() => openEditModal(t)}>
                  Edit
                </button>
                <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(t.id)}>
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
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">{editingTopic ? "Edit Topic" : "New Topic"}</h5>
                  <button type="button" className="btn-close" onClick={() => setShowModal(false)} />
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Name</label>
                    <input
                      className="form-control"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Prerequisites</label>
                    <select
                      multiple
                      className="form-select"
                      value={prereqIds}
                      onChange={(e) =>
                        setprereqIds([...e.target.selectedOptions].map((o) => Number(o.value)))
                      }
                    >
                      {topics
                        .filter((t) => t.id !== editingTopic?.id)
                        .map((t) => (
                          <option key={t.id} value={t.id}>
                            {t.name}
                          </option>
                        ))}
                    </select>
                  </div>
                </div>
                <div className="modal-footer">
                  <button className="btn btn-secondary" onClick={() => setShowModal(false)}>
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

export default ManageTopics;
