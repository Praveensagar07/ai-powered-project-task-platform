import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User } from '../types';
import { authService, LoginPayload, RegisterPayload } from '../services/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (updatedUser: User) => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const logout = useCallback(async () => {
    try {
      if (token) {
        await authService.logout();
      }
    } catch {
      // ignore network errors on logout
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_profile');
      setToken(null);
      setUser(null);
    }
  }, [token]);

  const refreshUser = useCallback(async () => {
    const currentToken = localStorage.getItem('access_token');
    if (!currentToken) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const profile = await authService.getMe();
      setUser(profile);
      localStorage.setItem('user_profile', JSON.stringify(profile));
    } catch (err) {
      console.warn('Session check failed or expired:', err);
      logout();
    } finally {
      setIsLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    refreshUser();

    // Listen for 401 expiration events fired from apiClient
    const handleAuthExpired = () => {
      logout();
    };

    window.addEventListener('auth:expired', handleAuthExpired);
    return () => window.removeEventListener('auth:expired', handleAuthExpired);
  }, [refreshUser, logout]);

  const login = async (payload: LoginPayload) => {
    setIsLoading(true);
    try {
      const response = await authService.login(payload);
      localStorage.setItem('access_token', response.token.access_token);
      localStorage.setItem('user_profile', JSON.stringify(response.user));
      setToken(response.token.access_token);
      setUser(response.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (payload: RegisterPayload) => {
    setIsLoading(true);
    try {
      const response = await authService.register(payload);
      localStorage.setItem('access_token', response.token.access_token);
      localStorage.setItem('user_profile', JSON.stringify(response.user));
      setToken(response.token.access_token);
      setUser(response.user);
    } finally {
      setIsLoading(false);
    }
  };

  const updateUser = (updated: User) => {
    setUser(updated);
    localStorage.setItem('user_profile', JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        register,
        logout,
        updateUser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
