import { useEffect, useState } from "react";
import api, { getCurrentUser } from "./api";
import { Routes, Route, Navigate, Link, useNavigate, useLocation } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ManageTopics from "./pages/ManageTopics";
import ManageAssignments from "./pages/ManageAssignments";
import RequireRole from "./components/RequireRole";
import ClassOverview from "./pages/ClassOverview";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getCurrentUser();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/dashboard">
          LMS
        </Link>
        <ul className="navbar-nav me-auto">
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
          <li className="nav-item">
            <Link className="nav-link" to="/assignments">
              Assignments
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/class-overview">
              Class Overview
            </Link>
          </li>
        </ul>
        {user && location.pathname !== "/login" && (
          <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
            Logout
          </button>
        )}
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
          <Route path="/assignments" element={<ManageAssignments />} />
          <Route path="/class-overview" element={<ClassOverview />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
