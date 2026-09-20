import { apiClient } from './api';
import { Task, TaskPriority, TaskStatus } from '../types';

export interface CreateTaskPayload {
  title: string;
  description?: string;
  project_id: string;
  assignee_id?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string;
  estimated_hours?: number;
}

export interface UpdateTaskPayload {
  title?: string;
  description?: string;
  project_id?: string;
  assignee_id?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string;
  estimated_hours?: number;
}

function mapBackendTask(t: any): Task {
  return {
    id: t.id,
    projectId: t.project_id,
    projectName: t.project_name,
    title: t.title,
    description: t.description || '',
    status: t.status,
    priority: t.priority,
    dueDate: t.due_date,
    assigneeId: t.assignee_id,
    assigneeName: t.assignee_name,
    tags: t.tags || 'task',
    estimatedHours: t.estimated_hours,
    createdAt: t.created_at,
    updatedAt: t.updated_at,
  };
}

export const taskService = {
  async listTasks(params?: {
    projectId?: string;
    status?: string;
    priority?: string;
    search?: string;
  }): Promise<Task[]> {
    const query = new URLSearchParams();
    if (params?.projectId && params.projectId !== 'all') query.append('project_id', params.projectId);
    if (params?.status && params.status !== 'all') query.append('status', params.status);
    if (params?.priority && params.priority !== 'all') query.append('priority', params.priority);
    if (params?.search) query.append('search', params.search);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const raw = await apiClient<any[]>(`/tasks${queryString}`);
    return raw.map(mapBackendTask);
  },

  async getTask(id: string): Promise<Task> {
    const raw = await apiClient<any>(`/tasks/${id}`);
    return mapBackendTask(raw);
  },

  async createTask(data: CreateTaskPayload): Promise<Task> {
    const raw = await apiClient<any>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return mapBackendTask(raw);
  },

  async createTasksBatch(tasks: CreateTaskPayload[]): Promise<Task[]> {
    const raw = await apiClient<any[]>('/tasks/batch', {
      method: 'POST',
      body: JSON.stringify(tasks),
    });
    return raw.map(mapBackendTask);
  },

  async updateTask(id: string, data: UpdateTaskPayload): Promise<Task> {
    const raw = await apiClient<any>(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return mapBackendTask(raw);
  },

  async updateTaskStatus(id: string, status: TaskStatus): Promise<Task> {
    const raw = await apiClient<any>(`/tasks/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
    return mapBackendTask(raw);
  },

  async updateTaskPriority(id: string, priority: TaskPriority): Promise<Task> {
    const raw = await apiClient<any>(`/tasks/${id}/priority`, {
      method: 'PATCH',
      body: JSON.stringify({ priority }),
    });
    return mapBackendTask(raw);
  },

  async deleteTask(id: string): Promise<{ message: string }> {
    return apiClient<{ message: string }>(`/tasks/${id}`, {
      method: 'DELETE',
    });
  },
};
