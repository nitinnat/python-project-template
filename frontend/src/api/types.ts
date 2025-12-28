/**
 * API type definitions
 * These should ideally be generated from OpenAPI spec
 */

export interface User {
  id: number;
  email: string;
  role: 'admin' | 'user' | 'readonly';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface FeatureFlag {
  key: string;
  enabled: boolean;
  description?: string;
  category?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}

export interface FeatureFlagUpdate {
  enabled: boolean;
  metadata?: Record<string, unknown>;
}

export interface ServiceHealth {
  status: 'healthy' | 'unhealthy' | 'degraded';
  latency_ms?: number;
  connections?: number;
  error?: string;
}

export interface SystemHealth {
  [service: string]: ServiceHealth;
}
