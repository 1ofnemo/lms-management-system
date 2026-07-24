import { useEffect, useState } from "react";
import { Routes, Route, Navigate, Link } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ManageTopics from "./pages/ManageTopics";
import RequireRole from "./components/RequireRole";

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <span className="navbar-brand">LMS</span>
        <ul className="navbar-nav">
          <li className="nav-item">
            <Link className="nav-link" to="/dashboard">
              Dashboard
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/topics">
              Topics
            </Link>
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
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />

        <Route element={<RequireRole />}>
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>

        <Route element={<RequireRole roles={["teacher", "admin"]} />}>
          <Route path="/topics" element={<ManageTopics />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
