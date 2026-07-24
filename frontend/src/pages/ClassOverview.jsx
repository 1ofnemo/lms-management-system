import { useEffect, useState } from "react";
import api from "../api";

const BADGE_CLASS = {
  advanced: "bg-success",
  average: "bg-warning text-dark",
  struggling: "bg-danger",
};

function ClassOverview() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    api.get("/progress").then((res) => setRows(res.data));
  }, []);

  const students = [
    ...new Map(rows.map((r) => [r.student_id, r.student_name])).entries(),
  ];
  const topics = [
    ...new Map(rows.map((r) => [r.topic_id, r.topic_name])).entries(),
  ];

  function cellFor(studentId, topicId) {
    return rows.find(
      (r) => r.student_id === studentId && r.topic_id === topicId,
    );
  }

  return (
    <div className="container py-4">
      <h1 className="h4 mb-3">Class Overview</h1>
      <table className="table text-center align-middle">
        <thead>
          <tr>
            <th>Student</th>
            {topics.map(([id, name]) => (
              <th key={id}>{name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {students.map(([id, name]) => (
            <tr key={id}>
              <td className="text-start">{name}</td>
              {topics.map(([topicId]) => {
                const cell = cellFor(id, topicId);
                return (
                  <td key={topicId}>
                    {cell && (
                      <span className={`badge ${BADGE_CLASS[cell.bucket]}`}>
                        {cell.bucket}
                      </span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ClassOverview;
