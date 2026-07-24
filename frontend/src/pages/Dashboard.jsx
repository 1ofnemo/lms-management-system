import { getCurrentUser } from "../api";

// ponytail: placeholder, real content (progress bars, mastery) lands in Sprint 4
function Dashboard() {
  const user = getCurrentUser();

  return (
    <div className="container py-4">
      <h1 className="h4">Dashboard</h1>
      <p>Logged in as {user?.role}.</p>
    </div>
  );
}

export default Dashboard;
