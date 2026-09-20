import React, { useState } from 'react';
import { Task, AISummarizeResponse } from '../../types';
import { Modal } from '../ui/Modal';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { aiService } from '../../services/ai';
import {
  Calendar,
  Clock,
  Sparkles,
  Tag,
  Check,
} from 'lucide-react';

interface TaskDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: Task | null;
}

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({
  isOpen,
  onClose,
  task,
}) => {
  const [summaryData, setSummaryData] = useState<AISummarizeResponse | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [error, setError] = useState('');

  if (!task) return null;

  const handleSummarize = async () => {
    setIsLoadingSummary(true);
    setError('');
    try {
      const res = await aiService.summarizeTask({
        task_id: task.id,
        title: task.title,
        description: task.description,
        priority: task.priority,
      });
      setSummaryData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate AI summary.');
    } finally {
      setIsLoadingSummary(false);
    }
  };

  const formattedDueDate = task.dueDate
    ? new Date(task.dueDate).toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      })
    : 'No due date';

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        setSummaryData(null);
        setError('');
        onClose();
      }}
      title="Task Details"
      subtitle={task.projectName ? `Project: ${task.projectName}` : undefined}
      maxWidth="xl"
    >
      <div className="space-y-6">
        {/* Status & Priority header */}
        <div className="flex items-center justify-between gap-3 flex-wrap pb-4 border-b border-gray-100 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <Badge status={task.status}>{task.status.replace('_', ' ')}</Badge>
            <Badge priority={task.priority}>{task.priority}</Badge>
          </div>

          <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>{formattedDueDate}</span>
            </span>
            {task.estimatedHours && (
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                <span>{task.estimatedHours}h est.</span>
              </span>
            )}
          </div>
        </div>

        {/* Task Title */}
        <div>
          <h2 className="text-lg font-bold text-gray-900 dark:text-white leading-snug">
            {task.title}
          </h2>
          {task.tags && (
            <div className="flex items-center gap-1.5 mt-2 flex-wrap">
              {task.tags.split(',').map((tag, idx) => (
                <span
                  key={idx}
                  className="flex items-center gap-1 text-[11px] font-medium text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2.5 py-0.5 rounded-full"
                >
                  <Tag className="w-2.5 h-2.5 text-gray-400" />
                  <span>{tag.trim()}</span>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Description */}
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Description
          </h4>
          <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/60 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
            {task.description || 'No detailed instructions recorded for this task.'}
          </div>
        </div>

        {/* AI Summarize section */}
        <div className="rounded-2xl p-4 bg-gradient-to-br from-indigo-50/70 via-purple-50/70 to-pink-50/50 dark:from-indigo-950/40 dark:via-purple-950/40 dark:to-pink-950/20 border border-indigo-100 dark:border-indigo-900/50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-indigo-700 dark:text-indigo-300 font-bold text-xs">
              <Sparkles className="w-4 h-4 text-indigo-500" />
              <span>AI Task Intelligence</span>
            </div>
            <Button
              size="sm"
              variant="ai"
              onClick={handleSummarize}
              isLoading={isLoadingSummary}
            >
              {summaryData ? 'Regenerate Summary' : 'Summarize with AI'}
            </Button>
          </div>

          {error && <p className="text-xs text-rose-500 font-medium mb-2">{error}</p>}

          {summaryData ? (
            <div className="space-y-3 pt-2 text-xs">
              <div>
                <span className="font-semibold text-gray-900 dark:text-white">Executive Summary:</span>
                <p className="mt-1 text-gray-700 dark:text-gray-300 leading-relaxed">
                  {summaryData.summary}
                </p>
              </div>

              {summaryData.key_deliverables?.length > 0 && (
                <div>
                  <span className="font-semibold text-gray-900 dark:text-white">Key Deliverables:</span>
                  <ul className="mt-1.5 space-y-1">
                    {summaryData.key_deliverables.map((item, i) => (
                      <li key={i} className="flex items-start gap-2 text-gray-600 dark:text-gray-300">
                        <Check className="w-3.5 h-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="p-2.5 rounded-lg bg-white/80 dark:bg-gray-900/80 border border-indigo-100/60 dark:border-indigo-900/40">
                <span className="font-semibold text-indigo-600 dark:text-indigo-400">Next Action:</span>
                <p className="mt-0.5 text-gray-800 dark:text-gray-200">
                  {summaryData.suggested_action}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Generate an instant executive briefing, key deliverable checklist, and actionable next steps for this task.
            </p>
          )}
        </div>

        <div className="flex justify-end pt-2">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
};
