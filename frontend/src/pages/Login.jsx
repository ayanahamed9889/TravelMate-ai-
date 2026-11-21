import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { getErrorMessage } from '../utils/errors';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await login(form.email.trim(), form.password);
      navigate('/dashboard');
    } catch (err) {
      setError(getErrorMessage(err, 'Login failed'));
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <form onSubmit={submit} className="glass-panel p-6 sm:p-8 w-full max-w-md space-y-4">
        <Link to="/" className="flex items-center gap-2 mb-2"><img src="/logo.svg" alt="" className="w-8 h-8" /><span className="font-bold text-primary">TravelMate AI</span></Link>
        <h1 className="text-2xl font-extrabold text-slate-900">Welcome back 👋</h1>
        <p className="text-sm text-slate-500 !mt-1">Sign in to your TravelMate account</p>
        <Input label="Email" type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <Input label="Password" type="password" autoComplete="current-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        {error && <p role="alert" className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>}
        <Button type="submit" variant="primary" className="w-full" disabled={loading}>{loading ? 'Signing in...' : 'Sign In'}</Button>
        <p className="text-xs text-center text-slate-500">No account? <Link to="/register" className="text-secondary font-bold">Register</Link></p>
      </form>
    </div>
  );
}
