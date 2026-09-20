import React from 'react';
import { ProjectPriority, ProjectStatus, TaskPriority, TaskStatus } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'status' | 'priority' | 'category' | 'ai';
  status?: ProjectStatus | TaskStatus;
  priority?: ProjectPriority | TaskPriority;
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  status,
  priority,
  size = 'md',
  className = '',
}) => {
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs font-medium',
  };

  let colorStyles = 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200';

  if (status) {
    switch (status) {
      case 'done':
      case 'completed':
        colorStyles = 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800';
        break;
      case 'in_progress':
      case 'active':
        colorStyles = 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800';
        break;
      case 'planning':
      case 'on_hold':
      case 'todo':
      default:
        colorStyles = 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800';
        break;
    }
  } else if (priority) {
    switch (priority) {
      case 'critical':
        colorStyles = 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800';
        break;
      case 'high':
        colorStyles = 'bg-orange-50 dark:bg-orange-950/40 text-orange-700 dark:text-orange-300 border border-orange-200 dark:border-orange-800';
        break;
      case 'medium':
        colorStyles = 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800';
        break;
      case 'low':
      default:
        colorStyles = 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700';
        break;
    }
  } else if (variant === 'ai') {
    colorStyles = 'bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/50 dark:to-purple-950/50 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 shadow-sm';
  }

  return (
    <span
      className={`inline-flex items-center rounded-full capitalize font-semibold tracking-wide ${sizeStyles[size]} ${colorStyles} ${className}`}
    >
      {children}
    </span>
  );
};
