import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { dashboardService } from '../services/dashboard';
import { aiService } from '../services/ai';
import { DashboardStats, AIProductivityResponse } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import { Button } from '../components/ui/Button';
import {
  FolderKanban,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Sparkles,
  Calendar,
  ArrowRight,
  Activity as ActivityIcon,
  Flame,
  CheckSquare,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [aiInsights, setAiInsights] = useState<AIProductivityResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [error, setError] = useState('');

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await dashboardService.getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleFetchAIInsights = async () => {
    setIsLoadingAI(true);
    try {
      const res = await aiService.getProductivitySuggestions();
      setAiInsights(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingAI(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-80 lg:col-span-2" />
          <Skeleton className="h-80" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center rounded-2xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto mb-3" />
        <h3 className="text-base font-bold text-gray-900 dark:text-white">Unable to Load Dashboard</h3>
        <p className="mt-1 text-xs text-rose-600 dark:text-rose-400 mb-4">{error}</p>
        <Button onClick={loadDashboardData} variant="outline" size="sm">
          Retry
        </Button>
      </div>
    );
  }

  const kpis = [
    {
      label: 'Active Projects',
      value: stats?.active_projects ?? 0,
      total: `${stats?.total_projects ?? 0} total`,
      icon: FolderKanban,
      color: 'text-indigo-600 dark:text-indigo-400',
      bg: 'bg-indigo-50 dark:bg-indigo-950/40',
    },
    {
      label: 'Completed Tasks',
      value: stats?.completed_tasks ?? 0,
      total: `${stats?.total_tasks ?? 0} total`,
      icon: CheckCircle2,
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-50 dark:bg-emerald-950/40',
    },
    {
      label: 'In Progress',
      value: stats?.in_progress_tasks ?? 0,
      total: `${stats?.todo_tasks ?? 0} in backlog`,
      icon: Clock,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-50 dark:bg-blue-950/40',
    },
    {
      label: 'Overdue Items',
      value: stats?.overdue_tasks ?? 0,
      total: 'Action needed',
      icon: AlertTriangle,
      color: 'text-rose-600 dark:text-rose-400',
      bg: 'bg-rose-50 dark:bg-rose-950/40',
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
            Developer Dashboard
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            Welcome back, <span className="font-semibold text-gray-800 dark:text-gray-200">{user?.name}</span>. Here is your platform overview.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/projects">
            <Button variant="outline" size="sm" leftIcon={<FolderKanban className="w-4 h-4" />}>
              View Projects
            </Button>
          </Link>
          <Link to="/tasks">
            <Button variant="primary" size="sm" leftIcon={<CheckSquare className="w-4 h-4" />}>
              Open Tasks
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => (
          <div
            key={idx}
            className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-5 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {kpi.label}
              </span>
              <div className={`p-2 rounded-xl ${kpi.bg}`}>
                <kpi.icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-gray-900 dark:text-white">
                {kpi.value}
              </span>
              <span className="text-xs font-medium text-gray-400">
                ({kpi.total})
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Productivity Score & AI Recommendation Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Productivity Score Banner */}
        <div className="rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 p-6 text-white shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-indigo-200 text-xs font-bold uppercase tracking-wider">
              <Flame className="w-4 h-4 text-amber-300" />
              <span>Productivity Score</span>
            </div>
            <span className="text-xs font-medium bg-white/20 px-2.5 py-0.5 rounded-full backdrop-blur-sm">
              {stats?.completion_rate}% Task Completion
            </span>
          </div>

          <div className="my-4">
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-black tracking-tight">
                {stats?.productivity_score ?? 85}
              </span>
              <span className="text-indigo-200 text-sm font-semibold">/ 100</span>
            </div>
            <p className="mt-2 text-xs text-indigo-100/80 leading-relaxed">
              Calculated from task delivery velocity, on-time milestones, and completion consistency.
            </p>
          </div>

          <div className="w-full bg-white/20 rounded-full h-2 overflow-hidden">
            <div
              className="bg-amber-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${stats?.productivity_score ?? 85}%` }}
            />
          </div>
        </div>

        {/* AI Productivity Copilot Box */}
        <div className="lg:col-span-2 rounded-2xl bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-50 dark:from-purple-950/30 dark:via-pink-950/20 dark:to-indigo-950/30 border border-purple-100 dark:border-purple-900/40 p-6 flex flex-col justify-between">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 text-purple-700 dark:text-purple-300 font-bold text-xs uppercase tracking-wider mb-1">
                <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span>AI Productivity Assistant</span>
              </div>
              <h3 className="text-base font-bold text-gray-900 dark:text-white">
                Intelligent Workload Analysis
              </h3>
            </div>
            <Button
              variant="ai"
              size="sm"
              onClick={handleFetchAIInsights}
              isLoading={isLoadingAI}
            >
              {aiInsights ? 'Refresh Insights' : 'Analyze Workload'}
            </Button>
          </div>

          <div className="my-3 text-xs leading-relaxed text-gray-700 dark:text-gray-300">
            {aiInsights ? (
              <div className="space-y-2">
                <p className="font-semibold text-indigo-700 dark:text-indigo-300">
                  Tip: {aiInsights.productivity_tip}
                </p>
                {aiInsights.bottleneck_warning && (
                  <p className="text-amber-600 dark:text-amber-400 font-medium">
                    ⚠️ {aiInsights.bottleneck_warning}
                  </p>
                )}
                <div>
                  <span className="font-semibold text-gray-900 dark:text-white">Recommended Focus:</span>
                  <ul className="list-disc list-inside mt-1 space-y-0.5 text-gray-600 dark:text-gray-400">
                    {aiInsights.focus_tasks.slice(0, 3).map((f: string, i: number) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400">
                Click "Analyze Workload" to receive personalized AI recommendations, priority bottleneck detection, and agile delivery tips tailored to your active projects.
              </p>
            )}
          </div>

          <div className="flex items-center justify-between text-[11px] text-purple-700 dark:text-purple-300 font-medium pt-2 border-t border-purple-200/50 dark:border-purple-800/40">
            <span>Powered by Backend AI Intelligence</span>
            <span className="capitalize">{aiInsights?.provider_mode || 'Active'}</span>
          </div>
        </div>
      </div>

      {/* Project Progress & Priority Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Progress List */}
        <div className="lg:col-span-2 rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-gray-900 dark:text-white">
              Project Progress
            </h3>
            <Link
              to="/projects"
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
            >
              <span>All Projects</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {stats?.projects_progress && stats.projects_progress.length > 0 ? (
            <div className="space-y-4">
              {stats.projects_progress.map((p) => (
                <div key={p.id} className="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <Link
                      to={`/projects/${p.id}`}
                      className="text-sm font-semibold text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400"
                    >
                      {p.name}
                    </Link>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                        {p.completed_tasks}/{p.total_tasks} tasks
                      </span>
                      <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                        {p.progress_percentage}%
                      </span>
                    </div>
                  </div>
                  <div className="h-1.5 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="bg-indigo-600 h-full rounded-full transition-all duration-300"
                      style={{ width: `${p.progress_percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400 py-6 text-center">No projects registered yet.</p>
          )}
        </div>

        {/* Priority & Upcoming Deadlines */}
        <div className="space-y-6">
          {/* Priority Distribution */}
          <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h3 className="text-base font-bold text-gray-900 dark:text-white mb-4">
              Priority Distribution
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                  <span className="text-gray-700 dark:text-gray-300">Critical</span>
                </span>
                <span className="font-bold">{stats?.priority_distribution.critical ?? 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-orange-500" />
                  <span className="text-gray-700 dark:text-gray-300">High</span>
                </span>
                <span className="font-bold">{stats?.priority_distribution.high ?? 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                  <span className="text-gray-700 dark:text-gray-300">Medium</span>
                </span>
                <span className="font-bold">{stats?.priority_distribution.medium ?? 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">Low</span>
                </span>
                <span className="font-bold">{stats?.priority_distribution.low ?? 0}</span>
              </div>
            </div>
          </div>

          {/* Upcoming Deadlines */}
          <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h3 className="text-base font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-500" />
              <span>Upcoming Deadlines</span>
            </h3>
            {stats?.upcoming_deadlines && stats.upcoming_deadlines.length > 0 ? (
              <div className="space-y-2.5">
                {stats.upcoming_deadlines.slice(0, 4).map((d) => (
                  <div key={d.id} className="text-xs p-2 rounded-lg bg-gray-50 dark:bg-gray-800/40">
                    <p className="font-semibold text-gray-900 dark:text-white truncate">
                      {d.title}
                    </p>
                    <div className="flex items-center justify-between mt-1 text-[11px] text-gray-500">
                      <span>{d.project_name}</span>
                      <span className="font-medium text-indigo-600 dark:text-indigo-400">
                        {d.due_date}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-400">No imminent deadlines.</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Activity Feed */}
      <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ActivityIcon className="w-4 h-4 text-indigo-500" />
            <h3 className="text-base font-bold text-gray-900 dark:text-white">Recent Activity</h3>
          </div>
          <Link
            to="/activity"
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
          >
            <span>View Full Audit Log</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        {stats?.recent_activities && stats.recent_activities.length > 0 ? (
          <div className="space-y-3">
            {stats.recent_activities.map((act) => (
              <div
                key={act.id}
                className="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                <div className="w-2 h-2 rounded-full bg-indigo-500 mt-2 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline justify-between gap-2">
                    <h5 className="text-xs font-bold text-gray-900 dark:text-white truncate">
                      {act.title}
                    </h5>
                    <span className="text-[10px] text-gray-400 flex-shrink-0">
                      {new Date(act.createdAt).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                  {act.description && (
                    <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400 line-clamp-1">
                      {act.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-gray-400 py-4 text-center">No recent activity.</p>
        )}
      </div>
    </div>
  );
};
