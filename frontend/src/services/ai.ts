import { apiClient } from './api';
import {
  AIProductivityResponse,
  AIProjectDescriptionResponse,
  AISummarizeResponse,
  AITaskGenerationResponse,
  AIStatus,
} from '../types';

export interface GenerateTasksPayload {
  project_id: string;
  project_name: string;
  project_description?: string;
  goals: string;
  target_date?: string;
}

export interface SummarizeTaskPayload {
  task_id?: string;
  title: string;
  description?: string;
  priority?: string;
}

export interface ProjectDescriptionPayload {
  title: string;
  category?: string;
  goals: string;
}

export const aiService = {
  async getStatus(): Promise<AIStatus> {
    return apiClient<AIStatus>('/ai/status');
  },

  async generateTasks(payload: GenerateTasksPayload): Promise<AITaskGenerationResponse> {
    return apiClient<AITaskGenerationResponse>('/ai/generate-tasks', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async summarizeTask(payload: SummarizeTaskPayload): Promise<AISummarizeResponse> {
    return apiClient<AISummarizeResponse>('/ai/summarize-task', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async generateProjectDescription(
    payload: ProjectDescriptionPayload
  ): Promise<AIProjectDescriptionResponse> {
    return apiClient<AIProjectDescriptionResponse>('/ai/project-description', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getProductivitySuggestions(): Promise<AIProductivityResponse> {
    return apiClient<AIProductivityResponse>('/ai/productivity-suggestions');
  },
};
