import { Link, Outlet } from 'react-router-dom';
import { LayoutDashboard, Settings, MessageSquare } from 'lucide-react';

export function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              <Link to="/" className="flex items-center gap-2">
                <LayoutDashboard className="w-6 h-6 text-primary-600" />
                <span className="text-xl font-bold text-gray-900">
                  One-Stop RAG
                </span>
              </Link>

              <div className="hidden md:flex items-center gap-4">
                <Link
                  to="/"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  to="/rag"
                  className="flex items-center gap-2 text-gray-700 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <MessageSquare className="w-4 h-4" />
                  Document Chat
                </Link>
                <Link
                  to="/admin"
                  className="flex items-center gap-2 text-gray-700 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Settings className="w-4 h-4" />
                  Admin
                </Link>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="px-4 py-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800 font-medium">
                  Auth disabled - Dev mode
                </p>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="h-[calc(100vh-4rem)]">
        <Outlet />
      </main>
    </div>
  );
}
