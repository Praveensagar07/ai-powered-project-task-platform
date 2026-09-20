import React, { useEffect, useState, useCallback } from 'react';
import { Task, Project, TaskStatus } from '../types';
import { taskService, CreateTaskPayload, UpdateTaskPayload } from '../services/tasks';
import { projectService } from '../services/projects';
import { useToast } from '../context/ToastContext';
import { TaskCard } from '../components/tasks/TaskCard';
import { TaskFormModal } from '../components/tasks/TaskFormModal';
import { TaskDetailModal } from '../components/tasks/TaskDetailModal';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import {
  CheckSquare,
  Plus,
  Search,
  Kanban,
  List,
  Circle,
  Clock,
  CheckCircle2,
} from 'lucide-react';

export const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [projectFilter, setProjectFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban');

  // Modals state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);
  const [selectedTaskForDetail, setSelectedTaskForDetail] = useState<Task | null>(null);

  const { addToast } = useToast();

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [allTasks, allProjects] = await Promise.all([
        taskService.listTasks({
          search: search || undefined,
          status: statusFilter,
          priority: priorityFilter,
          projectId: projectFilter,
        }),
        projectService.listProjects(),
      ]);
      setTasks(allTasks);
      setProjects(allProjects);
    } catch (err: any) {
      addToast('error', 'Error', err.message || 'Failed to load tasks.');
    } finally {
      setIsLoading(false);
    }
  }, [search, statusFilter, priorityFilter, projectFilter, addToast]);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadData();
    }, 250);
    return () => clearTimeout(timer);
  }, [loadData]);

  const handleStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    try {
      await taskService.updateTaskStatus(taskId, newStatus);
      loadData();
    } catch (err: any) {
      addToast('error', 'Update Failed', err.message);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await taskService.deleteTask(taskId);
      addToast('success', 'Task Deleted', 'Task removed successfully.');
      loadData();
    } catch (err: any) {
      addToast('error', 'Delete Failed', err.message);
    }
  };

  const handleCreateOrUpdateTask = async (data: CreateTaskPayload | UpdateTaskPayload) => {
    if (taskToEdit) {
      await taskService.updateTask(taskToEdit.id, data);
      addToast('success', 'Task Updated', 'Task has been updated.');
    } else {
      await taskService.createTask(data as CreateTaskPayload);
      addToast('success', 'Task Created', 'New task added.');
    }
    loadData();
  };

  // Group tasks for Kanban view
  const todoTasks = tasks.filter((t) => t.status === 'todo');
  const inProgressTasks = tasks.filter((t) => t.status === 'in_progress');
  const doneTasks = tasks.filter((t) => t.status === 'done');

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header and New Task */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
            Tasks
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            Track execution across projects with customizable Kanban and List views.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* View Toggle */}
          <div className="flex items-center rounded-xl bg-gray-100 dark:bg-gray-800 p-1 border border-gray-200/60 dark:border-gray-700/60">
            <button
              onClick={() => setViewMode('kanban')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                viewMode === 'kanban'
                  ? 'bg-white dark:bg-gray-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              <Kanban className="w-3.5 h-3.5" />
              <span>Kanban</span>
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                viewMode === 'list'
                  ? 'bg-white dark:bg-gray-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              <List className="w-3.5 h-3.5" />
              <span>List</span>
            </button>
          </div>

          <Button
            onClick={() => {
              setTaskToEdit(null);
              setIsFormOpen(true);
            }}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            New Task
          </Button>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center gap-3 p-4 rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search tasks by title, description, or project..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl text-sm border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Project filter */}
          <select
            value={projectFilter}
            onChange={(e) => setProjectFilter(e.target.value)}
            className="rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500 max-w-[160px] truncate"
          >
            <option value="all">All Projects</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>

          {/* Status filter (used in list view) */}
          {viewMode === 'list' && (
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Statuses</option>
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>
          )}

          {/* Priority filter */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          {(search || statusFilter !== 'all' || priorityFilter !== 'all' || projectFilter !== 'all') && (
            <button
              onClick={() => {
                setSearch('');
                setStatusFilter('all');
                setPriorityFilter('all');
                setProjectFilter('all');
              }}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline px-2"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Main Task View */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-80" />
          ))}
        </div>
      ) : tasks.length === 0 ? (
        <EmptyState
          icon={<CheckSquare className="w-6 h-6" />}
          title="No tasks match your criteria"
          description={
            search || priorityFilter !== 'all' || projectFilter !== 'all'
              ? 'Try adjusting your filters or search terms.'
              : 'Add your first task to kickstart your delivery sprint.'
          }
          actionLabel="Create Task"
          onAction={() => {
            setTaskToEdit(null);
            setIsFormOpen(true);
          }}
          actionIcon={<Plus className="w-4 h-4" />}
        />
      ) : viewMode === 'kanban' ? (
        /* Kanban Board Columns */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {/* Column: To Do */}
          <div className="rounded-2xl bg-gray-50 dark:bg-gray-900/40 border border-gray-100 dark:border-gray-800/80 p-4 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-gray-200/60 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <Circle className="w-4 h-4 text-gray-400" />
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">To Do</h3>
              </div>
              <span className="text-xs font-bold text-gray-500 bg-white dark:bg-gray-800 px-2 py-0.5 rounded-full border border-gray-100 dark:border-gray-700">
                {todoTasks.length}
              </span>
            </div>

            <div className="space-y-3 min-h-[120px]">
              {todoTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStatusChange={handleStatusChange}
                  onEdit={(t) => {
                    setTaskToEdit(t);
                    setIsFormOpen(true);
                  }}
                  onDelete={handleDeleteTask}
                  onViewDetails={(t) => setSelectedTaskForDetail(t)}
                  onSummarize={(t) => setSelectedTaskForDetail(t)}
                />
              ))}
              {todoTasks.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-6">No tasks in To Do.</p>
              )}
            </div>
          </div>

          {/* Column: In Progress */}
          <div className="rounded-2xl bg-gray-50 dark:bg-gray-900/40 border border-gray-100 dark:border-gray-800/80 p-4 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-gray-200/60 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-500" />
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">In Progress</h3>
              </div>
              <span className="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 px-2 py-0.5 rounded-full border border-blue-100 dark:border-blue-900/50">
                {inProgressTasks.length}
              </span>
            </div>

            <div className="space-y-3 min-h-[120px]">
              {inProgressTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStatusChange={handleStatusChange}
                  onEdit={(t) => {
                    setTaskToEdit(t);
                    setIsFormOpen(true);
                  }}
                  onDelete={handleDeleteTask}
                  onViewDetails={(t) => setSelectedTaskForDetail(t)}
                  onSummarize={(t) => setSelectedTaskForDetail(t)}
                />
              ))}
              {inProgressTasks.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-6">No tasks in progress.</p>
              )}
            </div>
          </div>

          {/* Column: Done */}
          <div className="rounded-2xl bg-gray-50 dark:bg-gray-900/40 border border-gray-100 dark:border-gray-800/80 p-4 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-gray-200/60 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">Completed</h3>
              </div>
              <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full border border-emerald-100 dark:border-emerald-900/50">
                {doneTasks.length}
              </span>
            </div>

            <div className="space-y-3 min-h-[120px]">
              {doneTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStatusChange={handleStatusChange}
                  onEdit={(t) => {
                    setTaskToEdit(t);
                    setIsFormOpen(true);
                  }}
                  onDelete={handleDeleteTask}
                  onViewDetails={(t) => setSelectedTaskForDetail(t)}
                  onSummarize={(t) => setSelectedTaskForDetail(t)}
                />
              ))}
              {doneTasks.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-6">No completed tasks.</p>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* List View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onStatusChange={handleStatusChange}
              onEdit={(t) => {
                setTaskToEdit(t);
                setIsFormOpen(true);
              }}
              onDelete={handleDeleteTask}
              onViewDetails={(t) => setSelectedTaskForDetail(t)}
              onSummarize={(t) => setSelectedTaskForDetail(t)}
            />
          ))}
        </div>
      )}

      {/* Modals */}
      <TaskFormModal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleCreateOrUpdateTask}
        taskToEdit={taskToEdit}
        projects={projects}
      />

      <TaskDetailModal
        isOpen={!!selectedTaskForDetail}
        onClose={() => setSelectedTaskForDetail(null)}
        task={selectedTaskForDetail}
      />
    </div>
  );
};
