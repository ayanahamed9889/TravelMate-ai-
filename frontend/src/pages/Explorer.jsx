import { useEffect, useState } from 'react';
import { Search, Bookmark, BookmarkCheck } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import Loader from '../components/ui/Loader';
import CoverImage from '../components/ui/CoverImage';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../utils/errors';
import { REGIONS } from '../utils/constants';
import { formatINR } from '../utils/formatters';

export default function Explorer() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [params] = useSearchParams();
  const urlQuery = params.get('q') || '';
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [places, setPlaces] = useState([]);
  const [query, setQuery] = useState(urlQuery);
  const [debounced, setDebounced] = useState(urlQuery);
  const [region, setRegion] = useState('All');
  const [saved, setSaved] = useState({});   // place_id -> saved row id

  // the top-bar search navigates here with ?q=
  useEffect(() => { setQuery(urlQuery); setDebounced(urlQuery); }, [urlQuery]);
  useEffect(() => { const t = setTimeout(() => setDebounced(query.trim()), 300); return () => clearTimeout(t); }, [query]);

  useEffect(() => {
    api.get('/places/saved').then((r) => setSaved(Object.fromEntries(r.data.map((s) => [s.place_id, s.id])))).catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true); setError('');
    api.get('/places', { params: { q: debounced || undefined, region: region !== 'All' ? region : undefined } })
      .then((r) => !cancelled && setPlaces(r.data))
      .catch((err) => { if (!cancelled) { setPlaces([]); setError(getErrorMessage(err, 'Could not load destinations.')); } })
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, [debounced, region]);

  const toggleSave = async (p) => {
    try {
      if (saved[p.id]) {
        await api.delete(`/places/saved/${saved[p.id]}`);
        setSaved((s) => { const n = { ...s }; delete n[p.id]; return n; });
        addToast(`Removed ${p.name} from saved`);
      } else {
        const { data } = await api.post('/places/saved', { place_id: p.id, name: p.name, state: p.state, category: p.region, description: p.tagline, image: p.image, avg_daily: p.avg_daily });
        setSaved((s) => ({ ...s, [p.id]: data.id }));
        addToast(`Saved ${p.name}`);
      }
    } catch (err) { addToast(getErrorMessage(err, 'Could not update saved places'), 'error'); }
  };

  return (
    <div className="page">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-2">Where to next in the world?</h1>
      <p className="text-sm text-slate-500 mb-6">Handpicked destinations across the globe with typical per-person daily costs (in ₹) and AI itineraries.</p>

      <div className="glass-panel p-4 mb-6 flex flex-col lg:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search destinations" placeholder="Search city, country or vibe (e.g. Japan, beaches)" className="field pl-9" />
        </div>
        <div className="flex gap-2 flex-wrap">
          {REGIONS.map((r) => (
            <button key={r} onClick={() => setRegion(r)} aria-pressed={region === r} className={`chip ${region === r ? 'chip-active' : 'chip-light'}`}>{r}</button>
          ))}
        </div>
      </div>

      {loading ? <Loader /> : error ? (
        <div className="glass-panel p-8 text-center text-red-600">{error}</div>
      ) : places.length === 0 ? (
        <div className="glass-panel p-10 text-center text-slate-500">No destinations match “{debounced}”. Try another word or region.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5 sm:gap-6">
          {places.map((p) => (
            <article key={p.id} className="glass-panel overflow-hidden group flex flex-col">
              <div className="relative h-44 overflow-hidden">
                <CoverImage src={p.image} lookup={{ q: `${p.name} ${p.state}`, kind: 'city' }} alt={p.name} seed={p.name} className="w-full h-full group-hover:scale-105 transition-transform" />
                <button onClick={() => toggleSave(p)} aria-pressed={!!saved[p.id]} aria-label={saved[p.id] ? `Unsave ${p.name}` : `Save ${p.name}`}
                  className="absolute top-3 right-3 w-9 h-9 rounded-full bg-white/95 flex items-center justify-center shadow hover:scale-105 transition-transform">
                  {saved[p.id] ? <BookmarkCheck size={18} className="text-secondary" /> : <Bookmark size={18} className="text-slate-500" />}
                </button>
                <span className="absolute bottom-3 left-3 text-[10px] font-bold uppercase tracking-wider bg-primary/80 text-white px-2.5 py-1 rounded-full">{p.region}</span>
              </div>
              <div className="p-4 flex-1 flex flex-col">
                <h2 className="font-bold text-slate-900">{p.name}</h2>
                <p className="text-xs text-slate-500">{p.state} · {p.tagline}</p>
                {p.best_time && <p className="text-xs text-slate-500 mt-1">Best time: {p.best_time}</p>}
                <div className="flex justify-between items-center mt-auto pt-3 border-t border-slate-100">
                  <p className="text-sm font-bold text-primary">{formatINR(p.avg_daily)}<span className="text-xs font-medium text-slate-400"> /day approx.</span></p>
                  <button onClick={() => navigate(`/planner?dest=${encodeURIComponent(p.name)}`)} className="chip bg-primary/5 text-primary hover:bg-primary/10">Plan with AI ✨</button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
