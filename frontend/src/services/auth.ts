import { apiClient } from './api';
import { User } from '../types';

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: {
    access_token: string;
    token_type: string;
    expires_in: number;
  };
}

export const authService = {
  async register(data: RegisterPayload): Promise<AuthResponse> {
    return apiClient<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async login(data: LoginPayload): Promise<AuthResponse> {
    return apiClient<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async logout(): Promise<void> {
    try {
      await apiClient('/auth/logout', { method: 'POST' });
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_profile');
    }
  },

  async getMe(): Promise<User> {
    return apiClient<User>('/auth/me');
  },

  async updateMe(data: Partial<User>): Promise<User> {
    return apiClient<User>('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
};
