import { useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Check, Sparkles } from 'lucide-react';
import api from '../api/axios';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../utils/errors';
import { PREFERENCES, BUDGET_TIERS, TRIP_TYPES, ACCOMMODATIONS, TRANSPORTS } from '../utils/constants';
import { daysBetween, formatDate, formatINR, todayISO } from '../utils/formatters';

const STEPS = ['Destination', 'Dates & Group', 'Vibe & Style', 'Budget', 'Review'];
const LAST = STEPS.length - 1;

export default function TripWizard() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [params] = useSearchParams();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const createdId = useRef(null);   // so retrying never creates a second draft
  const [form, setForm] = useState({
    destination: params.get('dest') || '', departure: '',
    start_date: '', end_date: '', travelers: 2, trip_type: 'Couple',
    preferences: [], accommodation: 'Hotel', transport: 'Flight',
    budget_tier: 'moderate', budget: 50000,
  });
  const set = (patch) => { setError(''); setForm((f) => ({ ...f, ...patch })); };

  const validate = (s) => {
    if (s === 0 && form.destination.trim().length < 2) return 'Enter a destination (at least 2 characters).';
    if (s === 1) {
      if (!form.start_date || !form.end_date) return 'Pick both a start and an end date.';
      if (form.start_date < todayISO()) return 'The start date cannot be in the past.';
      if (form.end_date < form.start_date) return 'The end date cannot be before the start date.';
      if (daysBetween(form.start_date, form.end_date) > 60) return 'Trips can be at most 60 days long.';
      if (!(form.travelers >= 1 && form.travelers <= 50)) return 'Travellers must be between 1 and 50.';
    }
    if (s === 3 && !(Number(form.budget) > 0)) return 'Enter a total budget greater than 0.';
    return '';
  };

  const next = () => {
    const msg = validate(step);
    if (msg) { setError(msg); return; }
    setStep((s) => Math.min(s + 1, LAST));
  };
  const back = () => { setError(''); setStep((s) => Math.max(s - 1, 0)); };

  const generate = async () => {
    for (let i = 0; i < LAST; i++) {
      const msg = validate(i);
      if (msg) { setStep(i); setError(msg); return; }
    }
    setLoading(true); setError('');
    try {
      if (!createdId.current) {
        const { data } = await api.post('/trips', {
          destination: form.destination.trim(), departure: form.departure.trim() || null,
          start_date: form.start_date, end_date: form.end_date, travelers: Number(form.travelers),
          trip_type: form.trip_type, preferences: form.preferences, accommodation: form.accommodation,
          transport: form.transport, budget: Number(form.budget), currency: 'INR', budget_tier: form.budget_tier,
        });
        createdId.current = data.id;
      }
      await api.post(`/trips/${createdId.current}/generate`, null, { timeout: 120000 });
      addToast('Itinerary generated!');
      navigate(`/trips/${createdId.current}`);
    } catch (err) {
      const msg = getErrorMessage(err, 'Failed to generate the itinerary');
      setError(msg);
      addToast(msg, 'error');
    } finally { setLoading(false); }
  };

  const togglePref = (p) => set({ preferences: form.preferences.includes(p) ? form.preferences.filter((x) => x !== p) : [...form.preferences, p] });
  const tier = BUDGET_TIERS.find((t) => t.key === form.budget_tier);
  const days = daysBetween(form.start_date, form.end_date);

  return (
    <div className="page max-w-[1100px]">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-1">Plan a Trip Anywhere in the World</h1>
      <p className="text-sm text-slate-500 mb-6">AI-driven planning in seconds.</p>

      <ol className="bg-indigo-50/60 rounded-2xl p-4 flex items-center justify-between gap-2 mb-6 border border-indigo-100">
        {STEPS.map((s, i) => (
          <li key={s} className="flex items-center gap-2 flex-1 min-w-0" aria-current={i === step ? 'step' : undefined}>
            <div className={`w-7 h-7 shrink-0 rounded-full flex items-center justify-center text-xs font-bold ${i <= step ? 'bg-primary text-white' : 'bg-white border border-slate-300 text-slate-400'}`}>
              {i < step ? <Check size={14} /> : i + 1}
            </div>
            <span className={`text-xs font-bold hidden md:block truncate ${i === step ? 'text-primary' : 'text-slate-500'}`}>{s}</span>
          </li>
        ))}
      </ol>

      <div className="glass-panel p-5 sm:p-8 space-y-5">
        {step === 0 && (
          <div className="grid sm:grid-cols-2 gap-4">
            <Input label="Destination" placeholder="e.g. Paris, Bali, Dubai or Jaipur" value={form.destination} maxLength={255} onChange={(e) => set({ destination: e.target.value })} autoFocus />
            <Input label="Travelling from (needed for travel cost)" placeholder="e.g. Delhi" value={form.departure} maxLength={255} onChange={(e) => set({ departure: e.target.value })} />
          </div>
        )}

        {step === 1 && (
          <div className="grid sm:grid-cols-2 gap-4">
            <Input label="Start Date" type="date" min={todayISO()} value={form.start_date} onChange={(e) => set({ start_date: e.target.value, end_date: form.end_date && form.end_date < e.target.value ? e.target.value : form.end_date })} />
            <Input label="End Date" type="date" min={form.start_date || todayISO()} value={form.end_date} onChange={(e) => set({ end_date: e.target.value })} />
            <Input label="Travellers" type="number" min={1} max={50} value={form.travelers} onChange={(e) => set({ travelers: e.target.value === '' ? '' : Math.max(0, parseInt(e.target.value, 10) || 0) })} />
            <div>
              <label className="label" htmlFor="trip-type">Trip type</label>
              <select id="trip-type" className="field" value={form.trip_type} onChange={(e) => set({ trip_type: e.target.value })}>
                {TRIP_TYPES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-5">
            <div>
              <span className="label">What do you enjoy? (pick any)</span>
              <div className="flex flex-wrap gap-2">
                {PREFERENCES.map((v) => (
                  <button key={v} type="button" aria-pressed={form.preferences.includes(v)} onClick={() => togglePref(v)} className={`chip ${form.preferences.includes(v) ? 'chip-active' : 'chip-light'}`}>{v}</button>
                ))}
              </div>
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="label" htmlFor="stay">Stay</label>
                <select id="stay" className="field" value={form.accommodation} onChange={(e) => set({ accommodation: e.target.value })}>{ACCOMMODATIONS.map((t) => <option key={t}>{t}</option>)}</select>
              </div>
              <div>
                <label className="label" htmlFor="transport">Main transport</label>
                <select id="transport" className="field" value={form.transport} onChange={(e) => set({ transport: e.target.value })}>{TRANSPORTS.map((t) => <option key={t}>{t}</option>)}</select>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div>
              <span className="label">Budget tier</span>
              <div className="grid sm:grid-cols-3 gap-3">
                {BUDGET_TIERS.map((t) => (
                  <button key={t.key} type="button" aria-pressed={form.budget_tier === t.key} onClick={() => set({ budget_tier: t.key })}
                    className={`text-left p-4 rounded-xl border transition-colors ${form.budget_tier === t.key ? 'border-primary bg-primary/5' : 'border-slate-200 hover:bg-slate-50'}`}>
                    <p className="font-bold text-primary">{t.label}</p>
                    <p className="text-xs text-slate-500">{t.range}</p>
                  </button>
                ))}
              </div>
            </div>
            <Input label="Total budget for the whole group (₹)" type="number" min={1} step={1000} value={form.budget} onChange={(e) => set({ budget: e.target.value === '' ? '' : Number(e.target.value) })} />
          </div>
        )}

        {step === LAST && (
          <dl className="grid sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
            {[
              ['Destination', form.destination],
              ['From', form.departure || '—'],
              ['Dates', `${formatDate(form.start_date)} → ${formatDate(form.end_date)} (${days} days)`],
              ['Travellers', `${form.travelers} · ${form.trip_type}`],
              ['Interests', form.preferences.join(', ') || 'Anything'],
              ['Stay / transport', `${form.accommodation} / ${form.transport}`],
              ['Budget', `${formatINR(form.budget)} (${tier?.label})`],
            ].map(([k, v]) => (
              <div key={k}><dt className="text-xs font-bold text-slate-400 uppercase tracking-wider">{k}</dt><dd className="font-semibold text-slate-800">{v}</dd></div>
            ))}
          </dl>
        )}

        {error && <p role="alert" className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>}

        <div className="flex justify-between pt-2">
          <Button variant="secondary" onClick={back} disabled={step === 0 || loading}>Back</Button>
          {step < LAST ? (
            <Button variant="primary" onClick={next}>Next</Button>
          ) : (
            <Button variant="primary" onClick={generate} disabled={loading}>
              <Sparkles size={16} /> {loading ? 'Generating… (up to a minute)' : 'Generate Itinerary'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
