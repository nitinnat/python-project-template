import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from '@/layouts/MainLayout';
import { AdminLayout } from '@/layouts/AdminLayout';
import { DashboardPage } from '@/pages/Dashboard';
import { FeatureFlagsPage } from '@/pages/admin/FeatureFlags';
import { ServiceHealthPage } from '@/pages/admin/ServiceHealth';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Main routes - no auth required */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<DashboardPage />} />
          </Route>

          {/* Admin routes - no auth required */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="/admin/feature-flags" replace />} />
            <Route path="feature-flags" element={<FeatureFlagsPage />} />
            <Route path="health" element={<ServiceHealthPage />} />
            <Route
              path="users"
              element={
                <div className="p-6">
                  <h1 className="text-3xl font-bold">User Management</h1>
                  <p className="mt-2 text-gray-600">Coming soon...</p>
                </div>
              }
            />
            <Route
              path="config"
              element={
                <div className="p-6">
                  <h1 className="text-3xl font-bold">System Configuration</h1>
                  <p className="mt-2 text-gray-600">Coming soon...</p>
                </div>
              }
            />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
