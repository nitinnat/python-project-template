import { Outlet } from 'react-router-dom';

export function AdminRoute() {
  // Auth removed - allow all access
  return <Outlet />;
}
