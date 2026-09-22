/**
 * Centralized API client module.
 * Automatically injects Bearer authorization token and parses responses/errors.
 */
function getBaseUrl(): string {
  const envUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '').trim();
  if (!envUrl) {
    return '/api';
  }
  // Strip trailing slashes
  const cleanUrl = envUrl.replace(/\/+$/, '');
  // If cleanUrl already ends with /api or /api/v1, use it directly; otherwise append /api
  if (cleanUrl.endsWith('/api') || cleanUrl.endsWith('/api/v1')) {
    return cleanUrl;
  }
  return `${cleanUrl}/api`;
}

const API_BASE_URL = getBaseUrl();

export class ApiError extends Error {
  status: number;
  details?: any;

  constructor(message: string, status: number, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_BASE_URL}${cleanEndpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized -> Clear session if token expired
    if (response.status === 401) {
      if (token && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_profile');
        window.dispatchEvent(new CustomEvent('auth:expired'));
      }
    }

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      let errorDetails: any = null;

      try {
        const errorJson = await response.json();
        if (errorJson?.error?.message) {
          errorMessage = errorJson.error.message;
        } else if (errorJson?.detail) {
          errorMessage = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
        errorDetails = errorJson?.error?.details || errorJson;
      } catch {
        // Response wasn't JSON
      }

      throw new ApiError(errorMessage, response.status, errorDetails);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error.message || 'Network error: unable to communicate with backend server.',
      0
    );
  }
}
