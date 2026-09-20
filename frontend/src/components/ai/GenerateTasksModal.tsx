import React, { useState } from 'react';
import { Project, AITaskItem, TaskPriority } from '../../types';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Badge } from '../ui/Badge';
import { aiService } from '../../services/ai';
import { Sparkles, RefreshCw, Plus, Edit2, AlertCircle } from 'lucide-react';

interface GenerateTasksModalProps {
  isOpen: boolean;
  onClose: () => void;
  project: Project | null;
  onSaveTasks: (tasks: Array<AITaskItem & { project_id: string }>) => Promise<void>;
}

export const GenerateTasksModal: React.FC<GenerateTasksModalProps> = ({
  isOpen,
  onClose,
  project,
  onSaveTasks,
}) => {
  const [goals, setGoals] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [generatedTasks, setGeneratedTasks] = useState<AITaskItem[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [suggestedApproach, setSuggestedApproach] = useState('');
  const [providerMode, setProviderMode] = useState('');
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [error, setError] = useState('');

  if (!project) return null;

  const handleGenerate = async () => {
    if (!goals.trim()) {
      setError('Please specify the primary project goals or milestones.');
      return;
    }

    setIsGenerating(true);
    setError('');
    try {
      const response = await aiService.generateTasks({
        project_id: project.id,
        project_name: project.name,
        project_description: project.description,
        goals: goals.trim(),
        target_date: targetDate || undefined,
      });

      setGeneratedTasks(response.tasks);
      setSuggestedApproach(response.suggested_approach);
      setProviderMode(response.provider_mode);
      // Default select all generated tasks
      setSelectedIndices(new Set(response.tasks.map((_, i) => i)));
    } catch (err: any) {
      setError(err.message || 'Failed to generate tasks with AI.');
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleSelect = (index: number) => {
    setSelectedIndices((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const selectAll = () => {
    if (selectedIndices.size === generatedTasks.length) {
      setSelectedIndices(new Set());
    } else {
      setSelectedIndices(new Set(generatedTasks.map((_, i) => i)));
    }
  };

  const updateTaskField = (index: number, field: keyof AITaskItem, value: any) => {
    setGeneratedTasks((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const handleSaveSelected = async () => {
    const selectedTasks = generatedTasks
      .filter((_, idx) => selectedIndices.has(idx))
      .map((t) => ({ ...t, project_id: project.id }));

    if (selectedTasks.length === 0) {
      setError('Please select at least one task to create.');
      return;
    }

    setIsSaving(true);
    setError('');
    try {
      await onSaveTasks(selectedTasks);
      onClose();
      // Reset
      setGeneratedTasks([]);
      setSelectedIndices(new Set());
      setGoals('');
    } catch (err: any) {
      setError(err.message || 'Failed to create selected tasks.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Generate Tasks with AI"
      subtitle={`Create an automated agile breakdown for: ${project.name}`}
      maxWidth="2xl"
    >
      <div className="space-y-5">
        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 text-xs font-medium border border-rose-200 dark:border-rose-800">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Input prompt form */}
        <div className="p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-800 space-y-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
              Project Goals & Deliverables
            </label>
            <textarea
              rows={2}
              className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g. Implement user authentication, setup database migrations, build responsive dashboard with dark mode"
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div className="w-48">
              <Input
                label="Target Milestone Date"
                type="date"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
              />
            </div>

            <div className="pt-5">
              <Button
                variant="ai"
                onClick={handleGenerate}
                isLoading={isGenerating}
                leftIcon={generatedTasks.length > 0 ? <RefreshCw className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
              >
                {generatedTasks.length > 0 ? 'Regenerate Tasks' : 'Generate Tasks with AI'}
              </Button>
            </div>
          </div>
        </div>

        {/* Review & Selection Section */}
        {generatedTasks.length > 0 && (
          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-gray-100 dark:border-gray-800">
              <div>
                <h4 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <span>AI Suggested Tasks</span>
                  <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                    ({selectedIndices.size} of {generatedTasks.length} selected)
                  </span>
                </h4>
                {suggestedApproach && (
                  <p className="mt-0.5 text-xs text-indigo-600 dark:text-indigo-400 italic">
                    Approach: {suggestedApproach}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={selectAll}
                  className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700"
                >
                  {selectedIndices.size === generatedTasks.length ? 'Deselect All' : 'Select All'}
                </button>
              </div>
            </div>

            {/* Generated Task Cards */}
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {generatedTasks.map((t, idx) => {
                const isSelected = selectedIndices.has(idx);
                const isEditing = editingIndex === idx;

                return (
                  <div
                    key={idx}
                    className={`rounded-xl border p-3.5 transition-all duration-200 ${
                      isSelected
                        ? 'border-indigo-300 dark:border-indigo-800 bg-indigo-50/30 dark:bg-indigo-950/20 shadow-sm'
                        : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 opacity-70'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelect(idx)}
                        className="mt-1 w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-700"
                      />

                      <div className="flex-1 min-w-0">
                        {isEditing ? (
                          <div className="space-y-2">
                            <Input
                              value={t.title}
                              onChange={(e) => updateTaskField(idx, 'title', e.target.value)}
                            />
                            <textarea
                              rows={2}
                              value={t.description}
                              onChange={(e) => updateTaskField(idx, 'description', e.target.value)}
                              className="w-full rounded-xl border border-gray-200 dark:border-gray-700 p-2 text-xs bg-white dark:bg-gray-800"
                            />
                            <div className="flex items-center gap-2">
                              <select
                                value={t.priority}
                                onChange={(e) => updateTaskField(idx, 'priority', e.target.value as TaskPriority)}
                                className="text-xs rounded-lg border border-gray-200 dark:border-gray-700 p-1 bg-white dark:bg-gray-800"
                              >
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="critical">Critical</option>
                              </select>
                              <Button size="sm" onClick={() => setEditingIndex(null)}>
                                Done
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="flex items-start justify-between gap-2">
                              <h5 className="text-sm font-semibold text-gray-900 dark:text-white">
                                {t.title}
                              </h5>
                              <div className="flex items-center gap-1.5 flex-shrink-0">
                                <Badge priority={t.priority} size="sm">
                                  {t.priority}
                                </Badge>
                                <button
                                  type="button"
                                  onClick={() => setEditingIndex(idx)}
                                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded"
                                  title="Edit task before adding"
                                >
                                  <Edit2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </div>
                            <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                              {t.description}
                            </p>
                            <div className="mt-2 flex items-center gap-3 text-[11px] text-gray-500 dark:text-gray-400">
                              <span>Est: {t.estimated_hours}h</span>
                              <span>Tags: {t.tags}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-800">
          <div className="text-xs text-gray-400">
            {providerMode && (
              <span className="capitalize">
                AI Mode: <strong className="text-indigo-600 dark:text-indigo-400">{providerMode}</strong>
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            {generatedTasks.length > 0 && (
              <Button
                variant="primary"
                onClick={handleSaveSelected}
                isLoading={isSaving}
                disabled={selectedIndices.size === 0}
                leftIcon={<Plus className="w-4 h-4" />}
              >
                Add {selectedIndices.size} Tasks to Project
              </Button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};
