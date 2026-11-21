import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark } from 'lucide-react';
import api from '../api/axios';
import Loader from '../components/ui/Loader';
import CoverImage from '../components/ui/CoverImage';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../utils/errors';
import { formatINR } from '../utils/formatters';

export default function SavedPlaces() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [places, setPlaces] = useState([]);

  const load = () => api.get('/places/saved').then((r) => setPlaces(r.data)).catch(() => setPlaces([])).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const remove = async (p) => {
    try { await api.delete(`/places/saved/${p.id}`); setPlaces((list) => list.filter((x) => x.id !== p.id)); addToast(`Removed ${p.name}`); }
    catch (err) { addToast(getErrorMessage(err, 'Could not remove the place'), 'error'); }
  };

  if (loading) return <Loader />;
  return (
    <div className="page">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-6">Saved Places</h1>
      {places.length === 0 ? (
        <div className="glass-panel p-10 text-center"><p className="text-slate-500 mb-3">No saved places yet. Tap the bookmark on any destination.</p><button onClick={() => navigate('/explore')} className="btn-primary">Explore Destinations</button></div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5 sm:gap-6">
          {places.map((p) => (
            <div key={p.id} className="glass-panel overflow-hidden">
              <CoverImage src={p.image} lookup={{ q: [p.name, p.state].filter(Boolean).join(' '), kind: 'city' }} alt={p.name} seed={p.name} className="w-full h-40" />
              <div className="p-4">
                <h4 className="font-bold text-slate-900">{p.name}</h4>
                <p className="text-xs text-slate-500">{[p.state, p.category].filter(Boolean).join(' · ')}</p>
                {p.avg_daily > 0 && <p className="text-sm font-bold text-primary mt-1">{formatINR(p.avg_daily)}<span className="text-xs font-medium text-slate-400"> /day approx.</span></p>}
                <div className="flex justify-between items-center mt-3">
                  <button onClick={() => navigate(`/planner?dest=${encodeURIComponent(p.name)}`)} className="chip bg-primary/5 text-primary hover:bg-primary/10">Plan with AI ✨</button>
                  <button onClick={() => remove(p)} className="text-xs font-bold text-red-500 flex items-center gap-1"><Bookmark size={12} /> Remove</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
