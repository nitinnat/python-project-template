export function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Welcome!</h2>
        <p className="text-gray-600">
          This is the main dashboard. Use the navigation menu to explore different
          features of the application.
        </p>

        <div className="mt-6 p-6 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            🚀 Quick Start
          </h3>
          <ul className="space-y-2 text-blue-800">
            <li>• Visit the <strong>Admin</strong> panel to manage feature flags and system health</li>
            <li>• Check the <strong>API Documentation</strong> at <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="underline">http://localhost:8000/docs</a></li>
            <li>• Explore the available services: MongoDB, Neo4j, PostgreSQL, Redis, RabbitMQ</li>
          </ul>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-semibold text-green-900">Status</h3>
            <p className="mt-2 text-green-700">All systems operational</p>
          </div>

          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h3 className="font-semibold text-purple-900">Environment</h3>
            <p className="mt-2 text-purple-700">Development Mode</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-900">Version</h3>
            <p className="mt-2 text-gray-700">v1.0.0</p>
          </div>
        </div>
      </div>
    </div>
  );
}
