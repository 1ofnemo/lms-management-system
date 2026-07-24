import { Navigate, Outlet } from "react-router-dom";
import { getCurrentUser } from "../api";

function RequireRole({ roles }) {
  const user = getCurrentUser();

  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role))
    return <Navigate to="/login" replace />;

  return <Outlet />;
}

export default RequireRole;
