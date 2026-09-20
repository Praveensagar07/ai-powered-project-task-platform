export type TaskStatus = 'todo' | 'in_progress' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

export type ProjectStatus = 'planning' | 'active' | 'completed' | 'on_hold';
export type ProjectPriority = 'low' | 'medium' | 'high' | 'critical';

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar: string;
  bio?: string;
  createdAt?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  priority: ProjectPriority;
  category: string;
  dueDate?: string;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
  totalTasks: number;
  completedTasks: number;
  progressPercentage: number;
}

export interface Task {
  id: string;
  projectId: string;
  projectName?: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueDate?: string;
  assigneeId?: string;
  assigneeName?: string;
  tags?: string;
  estimatedHours?: number;
  createdAt: string;
  updatedAt: string;
}

export type ActivityType =
  | 'project_created'
  | 'project_updated'
  | 'project_deleted'
  | 'task_created'
  | 'task_updated'
  | 'task_status_changed'
  | 'task_completed'
  | 'task_deleted'
  | 'ai_tasks_generated'
  | 'ai_task_summarized'
  | 'user_registered';

export interface Activity {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  type: ActivityType;
  title: string;
  description?: string;
  targetType: string;
  targetId?: string;
  createdAt: string;
}

export interface PriorityCount {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface StatusCount {
  todo: number;
  in_progress: number;
  done: number;
}

export interface ProjectProgress {
  id: string;
  name: string;
  status: string;
  priority: string;
  total_tasks: number;
  completed_tasks: number;
  progress_percentage: number;
}

export interface UpcomingDeadline {
  id: string;
  title: string;
  project_name: string;
  due_date: string;
  priority: string;
  status: string;
}

export interface DashboardStats {
  total_projects: number;
  active_projects: number;
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  todo_tasks: number;
  overdue_tasks: number;
  completion_rate: number;
  productivity_score: number;
  priority_distribution: PriorityCount;
  status_distribution: StatusCount;
  projects_progress: ProjectProgress[];
  upcoming_deadlines: UpcomingDeadline[];
  recent_activities: Activity[];
}

export interface AITaskItem {
  title: string;
  description: string;
  priority: TaskPriority;
  estimated_hours: number;
  tags: string;
}

export interface AITaskGenerationResponse {
  project_id: string;
  suggested_approach: string;
  tasks: AITaskItem[];
  provider_mode: string;
}

export interface AISummarizeResponse {
  summary: string;
  key_deliverables: string[];
  suggested_action: string;
  provider_mode: string;
}

export interface AIProjectDescriptionResponse {
  description: string;
  key_outcomes: string[];
  provider_mode: string;
}

export interface AIProductivityResponse {
  focus_tasks: string[];
  productivity_tip: string;
  bottleneck_warning?: string;
  provider_mode: string;
}

export interface AIStatus {
  status: string;
  provider: string;
  model: string;
  mode: string;
  is_custom_key_configured: boolean;
  info: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  message?: string;
}
