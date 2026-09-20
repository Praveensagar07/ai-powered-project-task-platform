import React from 'react';
import { Task, TaskStatus } from '../../types';
import { Badge } from '../ui/Badge';
import {
  Calendar,
  CheckCircle2,
  Clock,
  Circle,
  MoreVertical,
  Sparkles,
  Edit2,
  Trash2,
  Tag,
} from 'lucide-react';

interface TaskCardProps {
  task: Task;
  onStatusChange: (id: string, status: TaskStatus) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onViewDetails: (task: Task) => void;
  onSummarize?: (task: Task) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onStatusChange,
  onEdit,
  onDelete,
  onViewDetails,
  onSummarize,
}) => {
  const [menuOpen, setMenuOpen] = React.useState(false);

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case 'done':
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-blue-500 animate-pulse" />;
      case 'todo':
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const nextStatus: Record<TaskStatus, TaskStatus> = {
    todo: 'in_progress',
    in_progress: 'done',
    done: 'todo',
  };

  const formattedDate = task.dueDate
    ? new Date(task.dueDate).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      })
    : null;

  return (
    <div className="group relative rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-4 shadow-sm hover:shadow-md transition-all duration-200">
      <div className="flex items-start justify-between gap-2">
        {/* Quick status cycle button */}
        <button
          onClick={() => onStatusChange(task.id, nextStatus[task.status])}
          className="mt-0.5 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0"
          title={`Click to move to ${nextStatus[task.status].replace('_', ' ')}`}
          aria-label="Change status"
        >
          {getStatusIcon(task.status)}
        </button>

        {/* Task Title and Project */}
        <div className="flex-1 min-w-0">
          <div
            onClick={() => onViewDetails(task)}
            className="cursor-pointer font-semibold text-sm text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors line-clamp-2"
          >
            <span className={task.status === 'done' ? 'line-through text-gray-400 dark:text-gray-500' : ''}>
              {task.title}
            </span>
          </div>

          {task.projectName && (
            <p className="mt-0.5 text-[11px] font-medium text-indigo-600 dark:text-indigo-400 truncate">
              {task.projectName}
            </p>
          )}
        </div>

        {/* Action dropdown */}
        <div className="relative flex-shrink-0">
          <button
            onClick={() => setMenuOpen((prev) => !prev)}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            aria-label="Task options"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 mt-1 w-36 rounded-xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-xl py-1 z-20 animate-fade-in text-xs">
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    onViewDetails(task);
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                  <span>View Details</span>
                </button>
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    onEdit(task);
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                  <span>Edit</span>
                </button>
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    if (window.confirm(`Delete task "${task.title}"?`)) {
                      onDelete(task.id);
                    }
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Description Snippet */}
      {task.description && (
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 line-clamp-2 pl-7">
          {task.description}
        </p>
      )}

      {/* Tags and Badges */}
      <div className="mt-3.5 pt-2.5 border-t border-gray-50 dark:border-gray-800/80 flex items-center justify-between gap-2 flex-wrap text-xs">
        <div className="flex items-center gap-1.5 flex-wrap">
          <Badge priority={task.priority} size="sm">
            {task.priority}
          </Badge>
          {task.tags && (
            <span className="flex items-center gap-1 text-[10px] font-medium text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 px-2 py-0.5 rounded-full">
              <Tag className="w-2.5 h-2.5" />
              <span>{task.tags.split(',')[0]}</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {formattedDate && (
            <span className="flex items-center gap-1 text-[11px] font-medium text-gray-400">
              <Calendar className="w-3 h-3" />
              <span>{formattedDate}</span>
            </span>
          )}

          {onSummarize && (
            <button
              onClick={() => onSummarize(task)}
              className="p-1 rounded-md text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 transition-colors"
              title="Summarize with AI"
              aria-label="Summarize with AI"
            >
              <Sparkles className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
