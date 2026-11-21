import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Trash2 } from 'lucide-react';
import api from '../api/axios';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import BudgetChart from '../components/BudgetChart';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../utils/errors';
import { EXPENSE_CATEGORIES } from '../utils/constants';
import { formatINR } from '../utils/formatters';

const EMPTY = { item: '', category: 'Food', amount: '' };

export default function Budget() {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [target, setTarget] = useState(null);       // trip the expense modal is open for
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    api.get('/budget/overview')
      .then((r) => { setData(r.data); setError(''); })
      .catch((err) => setError(getErrorMessage(err, 'Could not load your budget.')))
      .finally(() => setLoading(false));
  }, []);
  useEffect(load, [load]);

  const addExpense = async (e) => {
    e.preventDefault();
    const amount = Number(form.amount);
    if (!form.item.trim() || !(amount > 0)) { addToast('Enter an item and an amount greater than 0', 'error'); return; }
    setSaving(true);
    try {
      await api.post(`/trips/${target.id}/expenses`, { item: form.item.trim(), category: form.category, amount });
      addToast('Expense added');
      setTarget(null); setForm(EMPTY); load();
    } catch (err) { addToast(getErrorMessage(err, 'Could not add the expense'), 'error'); }
    finally { setSaving(false); }
  };

  const removeExpense = async (tripId, expId) => {
    try { await api.delete(`/trips/${tripId}/expenses/${expId}`); load(); }
    catch (err) { addToast(getErrorMessage(err, 'Could not delete the expense'), 'error'); }
  };

  if (loading) return <Loader />;
  if (error) return <div className="page"><div className="glass-panel p-8 text-center text-red-600">{error}</div></div>;

  const trips = data?.trips || [];
  return (
    <div className="page">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-6">Budget Overview</h1>

      {trips.length === 0 ? (
        <div className="glass-panel p-10 text-center"><p className="text-slate-500 mb-3">Create a trip to start tracking its budget.</p><Link to="/planner" className="btn-primary">Plan a trip</Link></div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            {[['Total budget', data.total_budget_inr], ['AI estimates', data.total_estimated_inr], ['Spent so far', data.total_spent_inr]].map(([l, v]) => (
              <div key={l} className="glass-panel p-5"><p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{l}</p><p className="text-2xl font-extrabold text-slate-900">{formatINR(v)}</p></div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {trips.map((t) => (
              <div key={t.id} className="glass-panel p-5">
                <div className="flex justify-between items-start gap-3 mb-3">
                  <Link to={`/trips/${t.id}`} className="font-bold text-slate-900 capitalize hover:text-secondary">{t.title}</Link>
                  <button onClick={() => { setTarget(t); setForm(EMPTY); }} className="chip chip-light shrink-0"><Plus size={12} /> Expense</button>
                </div>
                <BudgetChart breakdown={t.breakdown} budget={t.budget_inr} label={t.spent_inr > 0 ? 'Spent' : 'AI estimate'} />
                {t.expenses.length > 0 && (
                  <ul className="mt-3 divide-y divide-slate-100 text-sm">
                    {t.expenses.map((x) => (
                      <li key={x.id} className="flex items-center justify-between py-2 gap-2">
                        <span className="min-w-0 truncate"><span className="font-medium text-slate-700">{x.item}</span> <span className="text-xs text-slate-400">· {x.category}</span></span>
                        <span className="flex items-center gap-2 shrink-0"><b>{formatINR(x.amount)}</b>
                          <button onClick={() => removeExpense(t.id, x.id)} aria-label={`Delete ${x.item}`} className="text-slate-300 hover:text-red-500"><Trash2 size={14} /></button></span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      <Modal open={!!target} onClose={() => setTarget(null)} title={`Add expense — ${target?.title || ''}`}>
        <form onSubmit={addExpense} className="space-y-4">
          <Input label="What was it?" value={form.item} maxLength={255} onChange={(e) => setForm({ ...form, item: e.target.value })} placeholder="e.g. Hotel deposit" required />
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label" htmlFor="exp-cat">Category</label>
              <select id="exp-cat" className="field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{EXPENSE_CATEGORIES.map((c) => <option key={c}>{c}</option>)}</select></div>
            <Input label="Amount (₹)" type="number" min={1} step="any" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
          </div>
          <div className="flex justify-end gap-2"><Button variant="ghost" onClick={() => setTarget(null)}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Add expense'}</Button></div>
        </form>
      </Modal>
    </div>
  );
}
