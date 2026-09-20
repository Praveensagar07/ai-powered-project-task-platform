import React, { useEffect, useState, useCallback } from 'react';
import { Activity as ActivityType } from '../types';
import { activityService } from '../services/activity';
import { useToast } from '../context/ToastContext';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import {
  Activity as ActivityIcon,
  FolderPlus,
  CheckCircle2,
  Clock,
  Sparkles,
  Trash2,
  Edit,
  UserPlus,
  Filter,
} from 'lucide-react';

export const Activity: React.FC = () => {
  const [activities, setActivities] = useState<ActivityType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('all');

  const { addToast } = useToast();

  const loadActivities = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await activityService.listActivities({
        type: typeFilter,
        limit: 100,
      });
      setActivities(data);
    } catch (err: any) {
      addToast('error', 'Error', err.message || 'Failed to load activity log.');
    } finally {
      setIsLoading(false);
    }
  }, [typeFilter, addToast]);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'project_created':
        return <FolderPlus className="w-4 h-4 text-indigo-500" />;
      case 'task_completed':
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case 'task_created':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'ai_tasks_generated':
      case 'ai_task_summarized':
        return <Sparkles className="w-4 h-4 text-purple-500" />;
      case 'project_deleted':
      case 'task_deleted':
        return <Trash2 className="w-4 h-4 text-rose-500" />;
      case 'user_registered':
        return <UserPlus className="w-4 h-4 text-teal-500" />;
      default:
        return <Edit className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
            Activity & Audit Trail
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            Chronological ledger of project modifications, task progression, and AI operations.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Events</option>
            <option value="project_created">Project Created</option>
            <option value="task_created">Task Created</option>
            <option value="task_completed">Task Completed</option>
            <option value="ai_tasks_generated">AI Tasks Generated</option>
            <option value="project_deleted">Project Deleted</option>
          </select>
        </div>
      </div>

      {/* Activity Timeline List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      ) : activities.length > 0 ? (
        <div className="relative border-l-2 border-gray-100 dark:border-gray-800 ml-4 space-y-6 pl-6 py-2">
          {activities.map((act) => (
            <div key={act.id} className="relative group">
              {/* Dot Icon */}
              <div className="absolute -left-[35px] top-1.5 flex items-center justify-center w-7 h-7 rounded-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 shadow-sm">
                {getActivityIcon(act.type)}
              </div>

              {/* Card */}
              <div className="p-4 rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 dark:text-white">
                      {act.title}
                    </h4>
                    {act.description && (
                      <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                        {act.description}
                      </p>
                    )}
                  </div>
                  <span className="text-[11px] text-gray-400 whitespace-nowrap">
                    {new Date(act.createdAt).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>

                <div className="mt-3 pt-2.5 border-t border-gray-50 dark:border-gray-800/80 flex items-center gap-2">
                  {act.userAvatar ? (
                    <img
                      src={act.userAvatar}
                      alt={act.userName}
                      className="w-5 h-5 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px] font-bold">
                      {act.userName?.[0] || 'U'}
                    </div>
                  )}
                  <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                    {act.userName}
                  </span>
                  <span className="text-[10px] font-mono text-gray-400 ml-auto bg-gray-50 dark:bg-gray-800 px-2 py-0.5 rounded">
                    {act.type}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<ActivityIcon className="w-6 h-6" />}
          title="No activity recorded yet"
          description="Actions performed across projects and tasks will be logged automatically here."
        />
      )}
    </div>
  );
};
