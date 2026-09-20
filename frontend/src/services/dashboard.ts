import { apiClient } from './api';
import { DashboardStats } from '../types';

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    return apiClient<DashboardStats>('/dashboard/stats');
  },
};
