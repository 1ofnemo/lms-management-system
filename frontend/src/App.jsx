import { useEffect, useState } from "react";
import api from "./api";

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <span className="navbar-brand">LMS</span>
        <ul className="navbar-nav">
          <li className="nav-item">
            <span className="nav-link">Dashboard</span>
          </li>
          <li className="nav-item">
            <span className="nav-link">Topics</span>
          </li>
          <li className="nav-item">
            <span className="nav-link">Assignments</span>
          </li>
        </ul>
      </div>
    </nav>
  );
}

function App() {
  const [apiStatus, setApiStatus] = useState("checking...");

  useEffect(() => {
    api
      .get("/health")
      .then((res) => setApiStatus(res.data.status))
      .catch(() => setApiStatus("unreachable"));
  }, []);

  return (
    <>
      <Navbar />
      <div className="container py-4">
        <p>
          Backend status:{" "}
          <span
            className={`badge ${apiStatus === "ok" ? "bg-success" : "bg-secondary"}`}
          >
            {apiStatus}
          </span>
        </p>
      </div>
    </>
  );
}

export default App;
