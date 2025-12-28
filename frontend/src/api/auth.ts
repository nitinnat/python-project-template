import apiClient from './client';
import type { LoginRequest, LoginResponse, RefreshTokenRequest, User } from './types';

/**
 * Authentication API calls
 */

export const authApi = {
  /**
   * Login with username and password
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // FastAPI OAuth2PasswordRequestForm expects form data
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * Refresh access token
   */
  async refresh(data: RefreshTokenRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/refresh', data);
    return response.data;
  },

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Register new user
   */
  async register(data: { email: string; password: string }): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },
};
