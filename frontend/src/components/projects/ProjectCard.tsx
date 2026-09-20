import React from 'react';
import { Link } from 'react-router-dom';
import { Project } from '../../types';
import { Badge } from '../ui/Badge';
import { Calendar, CheckCircle2, MoreVertical, Sparkles, Edit2, Trash2, ArrowRight } from 'lucide-react';

interface ProjectCardProps {
  project: Project;
  onEdit: (project: Project) => void;
  onDelete: (id: string) => void;
  onOpenAIModal?: (project: Project) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onEdit,
  onDelete,
  onOpenAIModal,
}) => {
  const [menuOpen, setMenuOpen] = React.useState(false);

  const formattedDate = project.dueDate
    ? new Date(project.dueDate).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : 'No deadline';

  return (
    <div className="relative group rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-5 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between">
      <div>
        {/* Header Badges */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge status={project.status}>{project.status.replace('_', ' ')}</Badge>
            <Badge priority={project.priority}>{project.priority}</Badge>
            <span className="text-[11px] font-medium text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 px-2 py-0.5 rounded-full border border-gray-100 dark:border-gray-800">
              {project.category}
            </span>
          </div>

          <div className="relative">
            <button
              onClick={() => setMenuOpen((prev) => !prev)}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              aria-label="Project actions"
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
                      onEdit(project);
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>
                  <button
                    onClick={() => {
                      setMenuOpen(false);
                      if (window.confirm(`Are you sure you want to delete "${project.name}"? All tasks will be deleted.`)) {
                        onDelete(project.id);
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

        {/* Title and Description */}
        <Link
          to={`/projects/${project.id}`}
          className="block group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors"
        >
          <h3 className="text-base font-bold text-gray-900 dark:text-white leading-snug line-clamp-1">
            {project.name}
          </h3>
        </Link>
        <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400 line-clamp-2 leading-relaxed min-h-[32px]">
          {project.description || 'No project description provided.'}
        </p>

        {/* Progress Bar */}
        <div className="mt-4 pt-3 border-t border-gray-50 dark:border-gray-800/80">
          <div className="flex items-center justify-between text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
              <span>
                {project.completedTasks} / {project.totalTasks} tasks
              </span>
            </span>
            <span>{project.progressPercentage}%</span>
          </div>
          <div className="h-1.5 w-full bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full transition-all duration-300"
              style={{ width: `${project.progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Footer Meta & Actions */}
      <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
          <Calendar className="w-3.5 h-3.5" />
          <span>{formattedDate}</span>
        </div>

        <div className="flex items-center gap-1.5">
          {onOpenAIModal && (
            <button
              onClick={() => onOpenAIModal(project)}
              className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 transition-colors"
              title="Generate tasks with AI"
            >
              <Sparkles className="w-3 h-3 text-indigo-500" />
              <span>AI Tasks</span>
            </button>
          )}

          <Link
            to={`/projects/${project.id}`}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <span>View</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </div>
    </div>
  );
};
