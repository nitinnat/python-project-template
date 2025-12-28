import { useAuth } from '@/hooks/useAuth';

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Welcome, {user?.email}!</h2>
        <p className="text-gray-600">
          This is the main dashboard. Use the navigation menu to explore different
          features of the application.
        </p>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
            <h3 className="font-semibold text-primary-900">Your Role</h3>
            <p className="mt-2 text-primary-700 capitalize">{user?.role}</p>
          </div>

          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-semibold text-green-900">Account Status</h3>
            <p className="mt-2 text-green-700">
              {user?.is_active ? 'Active' : 'Inactive'}
            </p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-900">Member Since</h3>
            <p className="mt-2 text-gray-700">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString()
                : 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
