import apiClient from './client';
import type { FeatureFlag, FeatureFlagUpdate, SystemHealth } from './types';

/**
 * Admin API calls
 */

export const adminApi = {
  /**
   * Get all feature flags
   */
  async getFeatureFlags(category?: string): Promise<{ flags: FeatureFlag[] }> {
    const params = category ? { category } : {};
    const response = await apiClient.get<{ flags: FeatureFlag[] }>(
      '/admin/feature-flags',
      { params }
    );
    return response.data;
  },

  /**
   * Update a feature flag
   */
  async updateFeatureFlag(
    key: string,
    update: FeatureFlagUpdate
  ): Promise<FeatureFlag> {
    const response = await apiClient.patch<FeatureFlag>(
      `/admin/feature-flags/${key}`,
      update
    );
    return response.data;
  },

  /**
   * Get system health status
   */
  async getSystemHealth(): Promise<SystemHealth> {
    const response = await apiClient.get<SystemHealth>('/admin/health');
    return response.data;
  },
};
