import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi } from '@/api/admin';
import { Badge } from '@/components/common/Badge';
import { Switch } from '@/components/common/Switch';
import { getErrorMessage } from '@/api/client';
import type { FeatureFlag } from '@/api/types';

/**
 * Group flags by category
 */
function groupBy<T extends Record<string, unknown>>(
  array: T[],
  key: keyof T
): Record<string, T[]> {
  return array.reduce((result, item) => {
    const group = String(item[key] || 'uncategorized');
    if (!result[group]) {
      result[group] = [];
    }
    result[group].push(item);
    return result;
  }, {} as Record<string, T[]>);
}

export function FeatureFlagsPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['admin', 'feature-flags'],
    queryFn: () => adminApi.getFeatureFlags(),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ key, enabled }: { key: string; enabled: boolean }) =>
      adminApi.updateFeatureFlag(key, { enabled }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'feature-flags'] });
    },
    onError: (error) => {
      alert(`Failed to update feature flag: ${getErrorMessage(error)}`);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading feature flags...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-red-600">
          Error loading feature flags: {getErrorMessage(error)}
        </div>
      </div>
    );
  }

  const flagsByCategory = groupBy(data?.flags || [], 'category');

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Feature Flags</h1>
        <p className="mt-2 text-gray-600">
          Manage runtime feature flags to enable or disable functionality without
          redeployment.
        </p>
      </div>

      {Object.entries(flagsByCategory).map(([category, categoryFlags]) => (
        <div key={category} className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 capitalize">
            {category}
          </h2>

          <div className="grid gap-4">
            {categoryFlags.map((flag: FeatureFlag) => (
              <div
                key={flag.key}
                className="bg-white border border-gray-200 rounded-lg p-4 flex items-center justify-between hover:shadow-md transition-shadow"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-medium text-gray-900">{flag.key}</h3>
                    <Badge variant={flag.enabled ? 'success' : 'secondary'}>
                      {flag.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                  {flag.description && (
                    <p className="text-sm text-gray-600 mt-1">{flag.description}</p>
                  )}
                  {flag.metadata?.requires && Array.isArray(flag.metadata.requires) && (
                    <div className="mt-2">
                      <span className="text-xs text-gray-500">Requires: </span>
                      <span className="text-xs text-gray-700">
                        {flag.metadata.requires.join(', ')}
                      </span>
                    </div>
                  )}
                </div>

                <Switch
                  checked={flag.enabled}
                  onCheckedChange={(enabled) =>
                    toggleMutation.mutate({ key: flag.key, enabled })
                  }
                  disabled={toggleMutation.isPending}
                />
              </div>
            ))}
          </div>
        </div>
      ))}

      {Object.keys(flagsByCategory).length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No feature flags found.</p>
        </div>
      )}
    </div>
  );
}
