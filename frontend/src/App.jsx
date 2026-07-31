import { useEffect, useState } from "react";
import api, { getCurrentUser } from "./api";
import {
  Routes,
  Route,
  Navigate,
  Link,
  useNavigate,
  useLocation,
} from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ManageTopics from "./pages/ManageTopics";
import ManageAssignments from "./pages/ManageAssignments";
import RequireRole from "./components/RequireRole";
import ClassOverview from "./pages/ClassOverview";
import MyAssignments from "./pages/MyAssignments";
import Submissions from "./pages/Submissions";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/topics", label: "Topics", roles: ["teacher", "admin"] },
  { to: "/assignments", label: "Assignments", roles: ["teacher", "admin"] },
  { to: "/class-overview", label: "Class Overview", roles: ["teacher", "admin"] },
  { to: "/my-assignments", label: "My Assignments", roles: ["student"] },
  { to: "/submissions", label: "Submissions", roles: ["teacher", "admin"] },
];

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getCurrentUser();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  const visibleItems = user
    ? NAV_ITEMS.filter((item) => !item.roles || item.roles.includes(user.role))
    : [];

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/dashboard">
          LMS
        </Link>
        <ul className="navbar-nav me-auto">
          {visibleItems.map((item) => (
            <li className="nav-item" key={item.to}>
              <Link className="nav-link" to={item.to}>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
        {user && location.pathname !== "/login" && (
          <button
            className="btn btn-outline-light btn-sm"
            onClick={handleLogout}
          >
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
          <Route path="/submissions" element={<Submissions />} />
        </Route>

        <Route element={<RequireRole roles={["student"]} />}>
          <Route path="/my-assignments" element={<MyAssignments />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
