import { useQuery } from '@tanstack/react-query';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { adminApi } from '@/api/admin';
import { getErrorMessage } from '@/api/client';
import type { ServiceHealth } from '@/api/types';

function getStatusIcon(status: string) {
  switch (status) {
    case 'healthy':
      return <CheckCircle className="w-6 h-6 text-green-500" />;
    case 'unhealthy':
      return <XCircle className="w-6 h-6 text-red-500" />;
    default:
      return <AlertCircle className="w-6 h-6 text-yellow-500" />;
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'healthy':
      return 'border-green-200 bg-green-50';
    case 'unhealthy':
      return 'border-red-200 bg-red-50';
    default:
      return 'border-yellow-200 bg-yellow-50';
  }
}

export function ServiceHealthPage() {
  const { data: health, isLoading, error } = useQuery({
    queryKey: ['admin', 'health'],
    queryFn: adminApi.getSystemHealth,
    refetchInterval: 5000, // Poll every 5 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading service health...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-red-600">
          Error loading service health: {getErrorMessage(error)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Service Health</h1>
        <p className="mt-2 text-gray-600">
          Real-time monitoring of all system services and their health status.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(health || {}).map(([service, status]: [string, ServiceHealth]) => (
          <div
            key={service}
            className={`border rounded-lg p-6 shadow-sm transition-all ${getStatusColor(
              status.status
            )}`}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold capitalize text-gray-900">
                {service}
              </h3>
              {getStatusIcon(status.status)}
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-medium text-gray-900 capitalize">
                  {status.status}
                </span>
              </div>

              {status.latency_ms !== undefined && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Latency:</span>
                  <span className="font-medium text-gray-900">
                    {status.latency_ms.toFixed(2)}ms
                  </span>
                </div>
              )}

              {status.connections !== undefined && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Connections:</span>
                  <span className="font-medium text-gray-900">{status.connections}</span>
                </div>
              )}

              {status.error && (
                <div className="mt-3 p-2 bg-white rounded border border-red-300">
                  <p className="text-red-600 text-xs break-words">
                    Error: {status.error}
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {Object.keys(health || {}).length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No services found.</p>
        </div>
      )}
    </div>
  );
}
