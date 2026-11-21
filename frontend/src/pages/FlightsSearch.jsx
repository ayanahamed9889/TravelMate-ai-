import { useEffect, useState } from 'react';
import { ArrowLeftRight, Plane } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import Loader from '../components/ui/Loader';
import FlightCard from '../components/FlightCard';
import { getErrorMessage } from '../utils/errors';
import { AIRPORTS } from '../utils/constants';
import { addDaysISO, todayISO } from '../utils/formatters';

export default function FlightsSearch() {
  const [params] = useSearchParams();
  const [form, setForm] = useState({
    from: (params.get('from') || 'DEL').toUpperCase(),
    to: (params.get('to') || 'JAI').toUpperCase(),
    date: params.get('date') || addDaysISO(todayISO(), 14),
    adults: 1,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [flights, setFlights] = useState(null);

  const search = async (f = form) => {
    if (!/^[A-Z]{3}$/.test(f.from) || !/^[A-Z]{3}$/.test(f.to)) { setError('Use 3-letter airport codes, e.g. DEL or BOM.'); return; }
    if (f.from === f.to) { setError('Origin and destination must be different.'); return; }
    if (f.date < todayISO()) { setError('Pick a date that is today or later.'); return; }
    setLoading(true); setError('');
    try {
      const r = await api.get('/flights/search', { params: { origin: f.from, destination: f.to, depart_date: f.date, adults: f.adults } });
      setFlights(r.data);
    } catch (err) { setFlights([]); setError(getErrorMessage(err, 'Flight search failed.')); }
    finally { setLoading(false); }
  };

  // links from a trip page (?from=&to=&date=) search straight away
  useEffect(() => { if (params.get('from') && params.get('to')) search(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  const set = (patch) => setForm((f) => ({ ...f, ...patch }));
  const code = (v) => v.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3);

  return (
    <div className="page">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-6">Flights Search</h1>
      <form onSubmit={(e) => { e.preventDefault(); search(); }} className="glass-panel p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[1fr_auto_1fr_1fr_90px_auto] gap-3 mb-6 items-end">
        <div><label className="label" htmlFor="f-from">From</label><input id="f-from" list="airports" className="field" value={form.from} onChange={(e) => set({ from: code(e.target.value) })} placeholder="DEL" /></div>
        <button type="button" onClick={() => set({ from: form.to, to: form.from })} className="hidden lg:flex h-[42px] w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-500 hover:bg-slate-50" aria-label="Swap airports"><ArrowLeftRight size={16} /></button>
        <div><label className="label" htmlFor="f-to">To</label><input id="f-to" list="airports" className="field" value={form.to} onChange={(e) => set({ to: code(e.target.value) })} placeholder="JAI" /></div>
        <div><label className="label" htmlFor="f-date">Date</label><input id="f-date" type="date" className="field" min={todayISO()} value={form.date} onChange={(e) => set({ date: e.target.value })} /></div>
        <div><label className="label" htmlFor="f-adults">Adults</label><input id="f-adults" type="number" min={1} max={9} className="field" value={form.adults} onChange={(e) => set({ adults: Math.min(9, Math.max(1, parseInt(e.target.value, 10) || 1)) })} /></div>
        <button type="submit" disabled={loading} className="btn-primary"><Plane size={16} /> Search</button>
        <datalist id="airports">{AIRPORTS.map(([c, n]) => <option key={c} value={c}>{n}</option>)}</datalist>
      </form>

      {error && <p role="alert" className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2 mb-4">{error}</p>}

      {loading ? <Loader text="Searching flights..." /> : flights === null ? (
        <p className="text-sm text-slate-500">Enter a route and date to search flights.</p>
      ) : flights.length === 0 && !error ? (
        <div className="glass-panel p-10 text-center text-slate-500">No flights found for this route and date.</div>
      ) : (
        <>
          {flights.length > 0 && flights.every((f) => f.source === 'demo') && (
            <p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 mb-4">
              These are <b>sample fares</b> for demonstration. Live airline data isn’t connected, so use “Check live” to see real prices.
            </p>
          )}
          <div className="space-y-3">{flights.map((f, i) => <FlightCard key={f.id} flight={f} index={i} date={form.date} />)}</div>
        </>
      )}
    </div>
  );
}
