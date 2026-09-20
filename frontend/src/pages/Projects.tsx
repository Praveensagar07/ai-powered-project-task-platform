import React, { useEffect, useState, useCallback } from 'react';
import { Project, AITaskItem } from '../types';
import { projectService, CreateProjectPayload, UpdateProjectPayload } from '../services/projects';
import { taskService } from '../services/tasks';
import { useToast } from '../context/ToastContext';
import { ProjectCard } from '../components/projects/ProjectCard';
import { ProjectFormModal } from '../components/projects/ProjectFormModal';
import { GenerateTasksModal } from '../components/ai/GenerateTasksModal';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { FolderKanban, Plus, Search } from 'lucide-react';

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');

  // Modals state
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [projectToEdit, setProjectToEdit] = useState<Project | null>(null);
  const [isAIModalOpen, setIsAIModalOpen] = useState(false);
  const [selectedProjectForAI, setSelectedProjectForAI] = useState<Project | null>(null);

  const { addToast } = useToast();

  const loadProjects = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await projectService.listProjects({
        search: search || undefined,
        status: statusFilter,
        priority: priorityFilter,
      });
      setProjects(data);
    } catch (err: any) {
      addToast('error', 'Error', err.message || 'Failed to fetch projects.');
    } finally {
      setIsLoading(false);
    }
  }, [search, statusFilter, priorityFilter, addToast]);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadProjects();
    }, 250);
    return () => clearTimeout(timer);
  }, [loadProjects]);

  const handleCreateOrUpdateProject = async (
    data: CreateProjectPayload | UpdateProjectPayload
  ) => {
    if (projectToEdit) {
      const updated = await projectService.updateProject(projectToEdit.id, data);
      addToast('success', 'Project Updated', `Project "${updated.name}" was updated.`);
    } else {
      const created = await projectService.createProject(data as CreateProjectPayload);
      addToast('success', 'Project Created', `Project "${created.name}" was created.`);
    }
    loadProjects();
  };

  const handleDeleteProject = async (id: string) => {
    try {
      await projectService.deleteProject(id);
      addToast('success', 'Project Deleted', 'Project and its tasks have been removed.');
      loadProjects();
    } catch (err: any) {
      addToast('error', 'Delete Failed', err.message);
    }
  };

  const handleSaveAITasks = async (tasks: Array<AITaskItem & { project_id: string }>) => {
    try {
      await taskService.createTasksBatch(
        tasks.map((t) => ({
          title: t.title,
          description: t.description,
          project_id: t.project_id,
          priority: t.priority,
          status: 'todo',
          tags: t.tags,
          estimated_hours: t.estimated_hours,
        }))
      );
      addToast('success', 'Tasks Created', `Added ${tasks.length} AI-generated tasks to the project.`);
      loadProjects();
    } catch (err: any) {
      addToast('error', 'Batch Creation Failed', err.message);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header & New Project action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
            Projects
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            Organize, monitor, and accelerate your engineering initiatives.
          </p>
        </div>

        <Button
          onClick={() => {
            setProjectToEdit(null);
            setIsFormModalOpen(true);
          }}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          New Project
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 p-4 rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search projects by name or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl text-sm border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Statuses</option>
            <option value="planning">Planning</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="on_hold">On Hold</option>
          </select>

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

          {(search || statusFilter !== 'all' || priorityFilter !== 'all') && (
            <button
              onClick={() => {
                setSearch('');
                setStatusFilter('all');
                setPriorityFilter('all');
              }}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline px-2"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onEdit={(p) => {
                setProjectToEdit(p);
                setIsFormModalOpen(true);
              }}
              onDelete={handleDeleteProject}
              onOpenAIModal={(p) => {
                setSelectedProjectForAI(p);
                setIsAIModalOpen(true);
              }}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<FolderKanban className="w-6 h-6" />}
          title="No projects found"
          description={
            search || statusFilter !== 'all' || priorityFilter !== 'all'
              ? 'Try modifying your search or filter settings to locate matching initiatives.'
              : 'Create your first project to start organizing tasks and unlocking AI productivity tools.'
          }
          actionLabel="Create Project"
          onAction={() => {
            setProjectToEdit(null);
            setIsFormModalOpen(true);
          }}
          actionIcon={<Plus className="w-4 h-4" />}
        />
      )}

      {/* Modals */}
      <ProjectFormModal
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        onSubmit={handleCreateOrUpdateProject}
        projectToEdit={projectToEdit}
      />

      <GenerateTasksModal
        isOpen={isAIModalOpen}
        onClose={() => setIsAIModalOpen(false)}
        project={selectedProjectForAI}
        onSaveTasks={handleSaveAITasks}
      />
    </div>
  );
};
