import { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import api from '../api/axios';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../utils/errors';

function Status({ label, on, onText, offText }) {
  return (
    <div className="flex items-center justify-between py-2.5 text-sm">
      <span className="font-medium text-slate-700">{label}</span>
      <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${on ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>{on ? onText : offText}</span>
    </div>
  );
}

export default function Settings() {
  const { user, updateUser, logout } = useAuth();
  const { addToast } = useToast();
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [health, setHealth] = useState(null);
  const [aiTest, setAiTest] = useState(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => { api.get('/health').then((r) => setHealth(r.data)).catch(() => setHealth(false)); }, []);

  const testAi = async () => {
    setTesting(true); setAiTest(null);
    try { setAiTest((await api.get('/health/ai', { timeout: 120000 })).data); }
    catch (err) { setAiTest({ ok: false, error: getErrorMessage(err) }); }
    finally { setTesting(false); }
  };

  const save = async (e) => {
    e.preventDefault();
    if (!name.trim()) { addToast('Name cannot be empty', 'error'); return; }
    setSaving(true);
    try {
      const { data } = await api.put('/auth/me', { name: name.trim() });
      updateUser(data);
      addToast('Settings saved');
    } catch (err) { addToast(getErrorMessage(err, 'Save failed'), 'error'); }
    finally { setSaving(false); }
  };

  return (
    <div className="page max-w-[720px] space-y-6">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">Settings</h1>

      <form onSubmit={save} className="glass-panel p-5 sm:p-6 space-y-4">
        <h2 className="font-bold text-slate-900">Profile</h2>
        <Input label="Name" value={name} maxLength={120} onChange={(e) => setName(e.target.value)} />
        <Input label="Email" value={user?.email || ''} readOnly disabled title="Email cannot be changed" />
        <p className="text-xs text-slate-500">All prices in TravelMate are shown in Indian Rupees (₹ INR), converted from local prices at approximate rates.</p>
        <div className="flex gap-3 flex-wrap">
          <Button type="submit" variant="primary" disabled={saving || name.trim() === (user?.name || '')}>{saving ? 'Saving...' : 'Save Changes'}</Button>
          <Button variant="secondary" onClick={logout}>Log out</Button>
        </div>
      </form>

      <div className="glass-panel p-5 sm:p-6">
        <h2 className="font-bold text-slate-900 mb-1">Data sources</h2>
        <p className="text-xs text-slate-500 mb-2">What is live and what is sample data in this installation.</p>
        {health === null ? <p className="text-sm text-slate-400">Checking…</p> : health === false ? (
          <p className="text-sm text-red-600">Cannot reach the backend. Is it running?</p>
        ) : (
          <div className="divide-y divide-slate-100">
            <Status label="AI itineraries & chat" on={!health.demo_mode} onText="Gemini (live)" offText="Demo mode" />
            <Status label="Hotels" on={health.geoapify} onText="Live listings" offText="Sample hotels" />
            <Status label="Restaurants" on={health.foursquare} onText="Foursquare" offText="OpenStreetMap" />
            <Status label="Flights" on={false} onText="" offText="Sample fares" />
            <Status label="Hotel photos" on={health.pexels} onText="Pexels" offText="Area photo only" />
            <Status label="Weather" on onText="Open-Meteo (live)" offText="" />
          </div>
        )}
        <div className="mt-4 pt-4 border-t border-slate-100">
          <Button variant="secondary" onClick={testAi} disabled={testing}>{testing ? 'Testing…' : 'Test Gemini connection'}</Button>
          {aiTest && (
            <p role="status" className={`mt-3 text-sm rounded-lg px-3 py-2 break-words ${aiTest.ok ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
              {aiTest.ok ? `Working ✔ model: ${aiTest.model} (${aiTest.key_type} key)` : `Failed: ${aiTest.error}`}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
