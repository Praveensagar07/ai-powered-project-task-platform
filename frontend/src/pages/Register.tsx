import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Layers, Sparkles, Lock, Mail, User, Briefcase, ArrowRight } from 'lucide-react';

export const Register: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Full Stack Developer');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !password) {
      setError('Please fill in all required fields.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setIsLoading(true);
    setError('');
    try {
      await register({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password,
        role: role.trim(),
      });
      addToast('success', 'Account created!', 'Welcome to your new AI productivity workspace.');
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Email may already be in use.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Branding Panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-gradient-to-br from-indigo-900 via-indigo-950 to-gray-950 p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_70%,rgba(99,102,241,0.2),transparent_50%)]" />

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
            <span>Join Innovation Hacks Week 4</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold leading-tight tracking-tight">
            Start managing projects with AI intelligence today.
          </h1>
          <p className="text-sm text-indigo-200/80 leading-relaxed">
            Create an account to track initiatives, generate agile backlogs with AI assistance, and monitor your personal developer productivity score.
          </p>
        </div>

        <div className="relative z-10 text-xs text-indigo-400/60">
          © 2026 Innovation Hacks Internship • Week 4 Final Implementation
        </div>
      </div>

      {/* Right Registration Form */}
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
              Create your account
            </h2>
            <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400">
              Set up your workspace credentials in under a minute.
            </p>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 text-xs font-semibold border border-rose-200 dark:border-rose-800">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              placeholder="Praveen Sagar"
              value={name}
              onChange={(e) => setName(e.target.value)}
              leftIcon={<User className="w-4 h-4" />}
              required
            />

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
              label="Professional Role"
              placeholder="e.g. Full Stack Developer, Tech Lead"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              leftIcon={<Briefcase className="w-4 h-4" />}
            />

            <Input
              label="Password (min 6 characters)"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-4 h-4" />}
              helperText="Encrypted with PBKDF2-HMAC-SHA256"
              required
            />

            <Button
              type="submit"
              variant="primary"
              isLoading={isLoading}
              className="w-full"
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Create Account
            </Button>
          </form>

          <div className="text-center pt-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Sign in instead
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
