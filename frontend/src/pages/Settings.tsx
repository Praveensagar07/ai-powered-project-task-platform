import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { authService } from '../services/auth';
import { aiService } from '../services/ai';
import { AIStatus } from '../types';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  User,
  Sparkles,
  Moon,
  Sun,
  Shield,
  Save,
  CheckCircle2,
  Info,
} from 'lucide-react';

export const Settings: React.FC = () => {
  const { user, updateUser } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { addToast } = useToast();

  const [name, setName] = useState(user?.name || '');
  const [role, setRole] = useState(user?.role || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [isSaving, setIsSaving] = useState(false);

  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);

  useEffect(() => {
    if (user) {
      setName(user.name);
      setRole(user.role);
      setBio(user.bio || '');
    }
  }, [user]);

  useEffect(() => {
    aiService
      .getStatus()
      .then(setAiStatus)
      .catch((err) => console.warn('AI status check failed:', err));
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const updated = await authService.updateMe({
        name: name.trim(),
        role: role.trim(),
        bio: bio.trim(),
      });
      updateUser(updated);
      addToast('success', 'Profile Updated', 'Your profile details have been saved.');
    } catch (err: any) {
      addToast('error', 'Update Failed', err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
          Settings & Preferences
        </h1>
        <p className="mt-1 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
          Manage your account credentials, AI integration provider, and workspace preferences.
        </p>
      </div>

      {/* Profile Section */}
      <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-gray-100 dark:border-gray-800">
          <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-gray-900 dark:text-white">Profile Information</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">Update your public display name and role.</p>
          </div>
        </div>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="flex items-center gap-4 mb-4">
            {user?.avatar ? (
              <img
                src={user.avatar}
                alt={user.name}
                className="w-16 h-16 rounded-2xl object-cover ring-2 ring-indigo-500/20"
              />
            ) : (
              <div className="w-16 h-16 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold text-xl">
                {user?.name?.[0] || 'U'}
              </div>
            )}
            <div>
              <h4 className="text-sm font-bold text-gray-900 dark:text-white">{user?.name}</h4>
              <p className="text-xs text-gray-400">{user?.email}</p>
              <Badge variant="default" size="sm" className="mt-1">
                {user?.role || 'Developer'}
              </Badge>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <Input
              label="Professional Role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
              Bio / Summary
            </label>
            <textarea
              rows={3}
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Tell your team about your core specialties..."
            />
          </div>

          <div className="flex justify-end pt-2">
            <Button
              type="submit"
              variant="primary"
              isLoading={isSaving}
              leftIcon={<Save className="w-4 h-4" />}
            >
              Save Profile
            </Button>
          </div>
        </form>
      </div>

      {/* AI Provider Status Card */}
      <div className="rounded-2xl bg-gradient-to-br from-indigo-50/50 via-purple-50/50 to-pink-50/30 dark:from-indigo-950/30 dark:via-purple-950/30 dark:to-pink-950/10 border border-indigo-100 dark:border-indigo-900/50 p-6 sm:p-8 shadow-sm space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span>AI Copilot Engine</span>
                {aiStatus?.mode === 'live' ? (
                  <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Live Provider Connected</span>
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800">
                    <Sparkles className="w-3 h-3" />
                    <span>Smart Heuristic Mode</span>
                  </span>
                )}
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Backend LLM provider configuration and operational status.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-xs">
          <div className="p-3.5 rounded-xl bg-white/80 dark:bg-gray-900/80 border border-gray-100 dark:border-gray-800">
            <span className="text-gray-400 font-medium">Provider:</span>
            <p className="font-bold text-gray-900 dark:text-white capitalize mt-0.5">
              {aiStatus?.provider || 'OpenAI / Generic'}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-white/80 dark:bg-gray-900/80 border border-gray-100 dark:border-gray-800">
            <span className="text-gray-400 font-medium">Target Model:</span>
            <p className="font-bold text-gray-900 dark:text-white mt-0.5">
              {aiStatus?.model || 'gpt-4o-mini'}
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-white/80 dark:bg-gray-900/80 border border-gray-100 dark:border-gray-800">
            <span className="text-gray-400 font-medium">Execution Mode:</span>
            <p className="font-bold text-gray-900 dark:text-white capitalize mt-0.5">
              {aiStatus?.mode || 'fallback-heuristic'}
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2.5 p-3 rounded-xl bg-white/70 dark:bg-gray-900/70 border border-indigo-100/60 dark:border-indigo-900/40 text-xs text-gray-600 dark:text-gray-300">
          <Info className="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" />
          <p>
            {aiStatus?.info ||
              'To connect a live OpenAI or Gemini API key, specify AI_API_KEY in your environment variables. The platform automatically maintains zero-crash continuity via fallback heuristics when keys are omitted.'}
          </p>
        </div>
      </div>

      {/* Appearance Section */}
      <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-6 sm:p-8 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-gray-900 dark:text-white">Appearance</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Select your preferred interface theme mode.
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={toggleTheme}
            leftIcon={theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
          >
            Switch to {theme === 'dark' ? 'Light' : 'Dark'} Mode
          </Button>
        </div>
      </div>

      {/* Security Info */}
      <div className="rounded-2xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-6 sm:p-8 shadow-sm space-y-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-gray-900 dark:text-white">Security & Cryptography</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Passwords are salted and hashed using PBKDF2-HMAC-SHA256 (100,000 rounds). Sessions are protected by signed JWTs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
