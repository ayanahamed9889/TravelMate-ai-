import { useCallback, useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import Loader from '../components/ui/Loader';
import HotelCard from '../components/HotelCard';
import { getErrorMessage } from '../utils/errors';
import { addDaysISO, todayISO } from '../utils/formatters';

export default function HotelsSearch() {
  const [params] = useSearchParams();
  const [form, setForm] = useState(() => {
    const ci = params.get('check_in') || addDaysISO(todayISO(), 7);
    return {
      city: params.get('city') || 'Paris',
      check_in: ci,
      check_out: params.get('check_out') || addDaysISO(ci, 2),
      adults: 2,
    };
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hotels, setHotels] = useState(null);

  const search = useCallback((f) => {
    if (f.city.trim().length < 2) { setError('Enter a city name.'); return; }
    if (f.check_out <= f.check_in) { setError('Check-out must be after check-in.'); return; }
    setLoading(true); setError('');
    api.get('/hotels/search', { params: { city: f.city.trim(), check_in: f.check_in, check_out: f.check_out, adults: f.adults } })
      .then((r) => setHotels(r.data))
      .catch((err) => { setHotels([]); setError(getErrorMessage(err, 'Hotel search failed.')); })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { search(form); /* first load only */ // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const set = (patch) => setForm((f) => ({ ...f, ...patch }));
  const sample = hotels?.length > 0 && hotels.every((h) => h.source === 'demo');

  return (
    <div className="page">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-6">Hotels Search</h1>
      <form onSubmit={(e) => { e.preventDefault(); search(form); }} className="glass-panel p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-6 items-end">
        <div className="lg:col-span-2"><label className="label" htmlFor="h-city">City</label><input id="h-city" className="field" value={form.city} onChange={(e) => set({ city: e.target.value })} placeholder="Enter city" /></div>
        <div><label className="label" htmlFor="h-in">Check-in</label><input id="h-in" type="date" className="field" min={todayISO()} value={form.check_in} onChange={(e) => set({ check_in: e.target.value, check_out: form.check_out <= e.target.value ? addDaysISO(e.target.value, 1) : form.check_out })} /></div>
        <div><label className="label" htmlFor="h-out">Check-out</label><input id="h-out" type="date" className="field" min={addDaysISO(form.check_in, 1)} value={form.check_out} onChange={(e) => set({ check_out: e.target.value })} /></div>
        <button type="submit" disabled={loading} className="btn-primary"><Search size={16} /> Search</button>
      </form>

      {error && <p role="alert" className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2 mb-4">{error}</p>}
      {sample && (
        <p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 mb-4">
          Showing <b>sample hotels</b> — add a Geoapify key in <code>backend/.env</code> for real listings. Sample prices are illustrative only.
        </p>
      )}

      {loading ? <Loader text="Searching hotels..." /> : hotels && hotels.length === 0 && !error ? (
        <div className="glass-panel p-10 text-center text-slate-500">No hotels found for “{form.city}”.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5 sm:gap-6">
          {(hotels || []).map((h, i) => <HotelCard key={h.id} hotel={h} index={i} />)}
        </div>
      )}
    </div>
  );
}
