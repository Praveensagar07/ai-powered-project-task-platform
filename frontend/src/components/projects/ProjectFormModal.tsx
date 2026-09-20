import React, { useState, useEffect } from 'react';
import { Project, ProjectPriority, ProjectStatus } from '../../types';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { CreateProjectPayload, UpdateProjectPayload } from '../../services/projects';
import { aiService } from '../../services/ai';
import { Sparkles } from 'lucide-react';

interface ProjectFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateProjectPayload | UpdateProjectPayload) => Promise<void>;
  projectToEdit?: Project | null;
}

export const ProjectFormModal: React.FC<ProjectFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  projectToEdit,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<ProjectStatus>('active');
  const [priority, setPriority] = useState<ProjectPriority>('medium');
  const [category, setCategory] = useState('Engineering');
  const [dueDate, setDueDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGeneratingDesc, setIsGeneratingDesc] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (projectToEdit) {
      setName(projectToEdit.name);
      setDescription(projectToEdit.description || '');
      setStatus(projectToEdit.status);
      setPriority(projectToEdit.priority);
      setCategory(projectToEdit.category || 'Engineering');
      setDueDate(projectToEdit.dueDate ? projectToEdit.dueDate.split('T')[0] : '');
    } else {
      setName('');
      setDescription('');
      setStatus('active');
      setPriority('medium');
      setCategory('Engineering');
      setDueDate('');
    }
    setError('');
  }, [projectToEdit, isOpen]);

  const handleAIDescription = async () => {
    if (!name.trim()) {
      setError('Please provide a project name first to generate a description.');
      return;
    }
    setIsGeneratingDesc(true);
    setError('');
    try {
      const res = await aiService.generateProjectDescription({
        title: name,
        category,
        goals: description || `Deliver full-stack features for ${name}`,
      });
      setDescription(res.description);
    } catch (err: any) {
      setError(err.message || 'Failed to generate AI description');
    } finally {
      setIsGeneratingDesc(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Project name is required.');
      return;
    }

    setIsSubmitting(true);
    setError('');
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
        status,
        priority,
        category,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save project.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={projectToEdit ? 'Edit Project' : 'Create New Project'}
      subtitle="Define project goals, priority, category, and target delivery date."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 text-xs font-medium border border-rose-200 dark:border-rose-800">
            {error}
          </div>
        )}

        <Input
          label="Project Name"
          placeholder="e.g. AI-Powered Project Platform"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
              Description
            </label>
            <button
              type="button"
              onClick={handleAIDescription}
              disabled={isGeneratingDesc}
              className="flex items-center gap-1 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 transition-colors"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isGeneratingDesc ? 'AI Drafting...' : 'Draft with AI'}</span>
            </button>
          </div>
          <textarea
            rows={3}
            className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Outline project objectives, architectural scope, or desired outcomes..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
              Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as ProjectStatus)}
              className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="planning">Planning</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="on_hold">On Hold</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as ProjectPriority)}
              className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
              Category
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g. Engineering, Product, DevOps"
              className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <Input
            label="Due Date"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100 dark:border-gray-800">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            {projectToEdit ? 'Save Changes' : 'Create Project'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
