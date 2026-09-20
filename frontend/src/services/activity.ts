import { apiClient } from './api';
import { Activity } from '../types';

function mapBackendActivity(a: any): Activity {
  return {
    id: a.id,
    userId: a.user_id,
    userName: a.user_name,
    userAvatar: a.user_avatar,
    type: a.type,
    title: a.title,
    description: a.description,
    targetType: a.target_type,
    targetId: a.target_id,
    createdAt: a.created_at,
  };
}

export const activityService = {
  async listActivities(params?: { limit?: number; type?: string }): Promise<Activity[]> {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.type && params.type !== 'all') query.append('type', params.type);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const raw = await apiClient<any[]>(`/activity${queryString}`);
    return raw.map(mapBackendActivity);
  },
};
