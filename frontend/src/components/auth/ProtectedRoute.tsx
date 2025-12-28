import { Outlet } from 'react-router-dom';

export function ProtectedRoute() {
  // Auth removed - allow all access
  return <Outlet />;
}
