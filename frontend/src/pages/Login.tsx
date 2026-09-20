import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Layers, Sparkles, Lock, Mail, ArrowRight, ShieldCheck } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all required fields.');
      return;
    }

    setIsLoading(true);
    setError('');
    try {
      await login({ email, password });
      addToast('success', 'Welcome back!', 'Successfully signed in to your workspace.');
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify your email and password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFillDemo = () => {
    setEmail('praveen@example.com');
    setPassword('Password123!');
    setError('');
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Marketing / Branding Panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-gradient-to-br from-indigo-900 via-indigo-950 to-gray-950 p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(99,102,241,0.2),transparent_50%)]" />

        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 text-white shadow-lg">
              <Layers className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight">
                TaskPulse<span className="text-indigo-400">.ai</span>
              </span>
              <span className="block text-[10px] text-indigo-300 font-medium tracking-wide">
                Innovation Hacks • Full Stack Development Final Project
              </span>
            </div>
          </div>
        </div>

        <div className="relative z-10 max-w-md space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-400/20 text-indigo-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Driven Agile Productivity</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold leading-tight tracking-tight">
            Supercharge engineering execution with intelligent task workflows.
          </h1>
          <p className="text-sm text-indigo-200/80 leading-relaxed">
            Consolidating project architecture, automated AI milestone breakdowns, real-time telemetry metrics, and secure access controls into one unified application.
          </p>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-indigo-800/40 text-xs">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>JWT & PBKDF2 Security</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span>Interactive AI Task Suite</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-xs text-indigo-400/60">
          © 2026 Innovation Hacks Internship • Week 4 Final Implementation
        </div>
      </div>

      {/* Right Login Form Panel */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12 bg-white dark:bg-gray-950">
        <div className="w-full max-w-md space-y-8 animate-fade-in">
          <div>
            <div className="lg:hidden flex items-center gap-2 mb-6">
              <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center">
                <Layers className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg text-gray-900 dark:text-white">TaskPulse.ai</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
              Sign in to your account
            </h2>
            <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400">
              Welcome back! Please enter your credentials to access your workspace.
            </p>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 text-xs font-semibold border border-rose-200 dark:border-rose-800">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-4 h-4" />}
              required
            />

            <Button
              type="submit"
              variant="primary"
              isLoading={isLoading}
              className="w-full"
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In
            </Button>
          </form>

          {/* Demo account quick filler */}
          <div className="pt-2">
            <button
              type="button"
              onClick={handleFillDemo}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 text-xs font-semibold rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors border border-indigo-200/60 dark:border-indigo-800/60"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
              <span>Fill Demo Credentials (praveen@example.com)</span>
            </button>
          </div>

          <div className="text-center pt-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Don't have an account yet?{' '}
              <Link
                to="/register"
                className="font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
