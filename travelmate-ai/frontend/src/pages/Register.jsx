import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { getErrorMessage } from '../utils/errors';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return; }
    setLoading(true);
    try {
      await register({ ...form, name: form.name.trim(), email: form.email.trim() });
      navigate('/dashboard');
    } catch (err) {
      setError(getErrorMessage(err, 'Registration failed'));
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <form onSubmit={submit} className="glass-panel p-6 sm:p-8 w-full max-w-md space-y-4">
        <Link to="/" className="flex items-center gap-2 mb-2"><img src="/logo.svg" alt="" className="w-8 h-8" /><span className="font-bold text-primary">TravelMate AI</span></Link>
        <h1 className="text-2xl font-extrabold text-slate-900">Create account ✨</h1>
        <p className="text-sm text-slate-500 !mt-1">Start planning smarter journeys</p>
        <Input label="Full Name" autoComplete="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required maxLength={120} />
        <Input label="Email" type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <Input label="Password" type="password" autoComplete="new-password" minLength={6} maxLength={72} placeholder="At least 6 characters" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        {error && <p role="alert" className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>}
        <Button type="submit" variant="primary" className="w-full" disabled={loading}>{loading ? 'Creating...' : 'Create Account'}</Button>
        <p className="text-xs text-center text-slate-500">Already registered? <Link to="/login" className="text-secondary font-bold">Sign In</Link></p>
      </form>
    </div>
  );
}
