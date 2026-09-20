import { apiClient } from './api';
import { Project, ProjectPriority, ProjectStatus } from '../types';

export interface CreateProjectPayload {
  name: string;
  description?: string;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  category?: string;
  due_date?: string;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  category?: string;
  due_date?: string;
}

function mapBackendProject(p: any): Project {
  return {
    id: p.id,
    name: p.name,
    description: p.description || '',
    status: p.status,
    priority: p.priority,
    category: p.category || 'Engineering',
    dueDate: p.due_date,
    ownerId: p.owner_id,
    createdAt: p.created_at,
    updatedAt: p.updated_at,
    totalTasks: p.total_tasks || 0,
    completedTasks: p.completed_tasks || 0,
    progressPercentage: p.progress_percentage || 0,
  };
}

export const projectService = {
  async listProjects(params?: {
    status?: string;
    priority?: string;
    search?: string;
  }): Promise<Project[]> {
    const query = new URLSearchParams();
    if (params?.status && params.status !== 'all') query.append('status', params.status);
    if (params?.priority && params.priority !== 'all') query.append('priority', params.priority);
    if (params?.search) query.append('search', params.search);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const raw = await apiClient<any[]>(`/projects${queryString}`);
    return raw.map(mapBackendProject);
  },

  async getProject(id: string): Promise<Project> {
    const raw = await apiClient<any>(`/projects/${id}`);
    return mapBackendProject(raw);
  },

  async createProject(data: CreateProjectPayload): Promise<Project> {
    const raw = await apiClient<any>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return mapBackendProject(raw);
  },

  async updateProject(id: string, data: UpdateProjectPayload): Promise<Project> {
    const raw = await apiClient<any>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return mapBackendProject(raw);
  },

  async deleteProject(id: string): Promise<{ message: string }> {
    return apiClient<{ message: string }>(`/projects/${id}`, {
      method: 'DELETE',
    });
  },
};
