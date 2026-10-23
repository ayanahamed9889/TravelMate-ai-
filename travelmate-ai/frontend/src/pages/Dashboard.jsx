import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Map, Compass, Sparkles, Wallet, ChevronRight } from 'lucide-react';
import api from '../api/axios';
import Loader from '../components/ui/Loader';
import CoverImage from '../components/ui/CoverImage';
import TripCard from '../components/TripCard';
import { useAuth } from '../hooks/useAuth';
import { formatINR } from '../utils/formatters';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ upcoming: 0, destinations: 0, saved: 0, total_budget: 0 });
  const [trips, setTrips] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    Promise.all([
      api.get('/trips/stats').then((r) => r.data).catch(() => null),
      api.get('/trips', { params: { status: 'active', limit: 3 } }).then((r) => r.data.items).catch(() => []),
      api.get('/places/recommended', { params: { limit: 3 } }).then((r) => r.data).catch(() => []),
    ]).then(([s, t, r]) => {
      if (s) setStats(s);
      setTrips(t || []);
      setRecommendations(r || []);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader text="Loading your dashboard..." />;

  const cards = [
    { label: 'UPCOMING TRIPS', value: stats.upcoming, icon: Plane, color: 'text-primary' },
    { label: 'DESTINATIONS PLANNED', value: stats.destinations, icon: Map, color: 'text-secondary' },
    { label: 'SAVED PLACES', value: stats.saved, icon: Compass, color: 'text-primary' },
    { label: 'UPCOMING BUDGET', value: formatINR(stats.total_budget), icon: Wallet, color: 'text-tertiary' },
  ];

  return (
    <div className="page space-y-8">
      <div className="bg-primary rounded-3xl p-6 sm:p-8 relative overflow-hidden text-white shadow-float">
        <div className="absolute -right-16 -top-16 w-64 h-64 rounded-full bg-secondary/20 blur-3xl" aria-hidden="true" />
        <div className="relative z-10 max-w-xl">
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-3">
            Welcome back, <span className="text-secondary">{user?.name?.split(' ')[0] || 'Traveler'}</span> ✨
          </h1>
          <p className="text-slate-300 text-sm mb-6">Your journeys, budget and AI insights are all in one place.</p>
          <button onClick={() => navigate('/planner')} className="btn-primary">Plan a New Trip</button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {cards.map((s) => (
          <div key={s.label} className="glass-panel p-4 sm:p-5">
            <div className={`p-2 rounded-lg bg-slate-50 ${s.color} w-fit mb-3`}><s.icon size={20} /></div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">{s.label}</p>
            <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900">{s.value}</h3>
          </div>
        ))}
      </div>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900">Upcoming Itineraries</h2>
          <button onClick={() => navigate('/trips')} className="text-sm font-semibold text-primary hover:underline flex items-center gap-1">View All <ChevronRight size={14} /></button>
        </div>
        <div className="space-y-4">
          {trips.length === 0 ? (
            <div className="glass-panel p-8 text-center">
              <p className="text-slate-500 mb-3">No upcoming trips yet.</p>
              <button onClick={() => navigate('/planner')} className="btn-primary">Create your first trip</button>
            </div>
          ) : trips.map((t) => <TripCard key={t.id} trip={t} />)}
        </div>
      </section>

      <section>
        <div className="flex justify-between items-end mb-4">
          <div>
            <p className="text-xs font-bold text-secondary uppercase tracking-wider flex items-center gap-1 mb-1"><Sparkles size={12} /> Recommended</p>
            <h2 className="text-xl font-bold text-slate-900">Destinations For You</h2>
          </div>
          <button onClick={() => navigate('/explore')} className="text-sm font-semibold text-primary hover:underline">Explore All</button>
        </div>
        {recommendations.length === 0 ? (
          <div className="glass-panel p-8 text-center text-slate-500">Recommendations are unavailable right now.</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
            {recommendations.slice(0, 3).map((p) => (
              <button key={p.id} className="glass-panel overflow-hidden group text-left" onClick={() => navigate(`/planner?dest=${encodeURIComponent(p.name)}`)}>
                <div className="relative h-40 overflow-hidden">
                  <CoverImage src={p.image} lookup={{ q: `${p.name} ${p.state}`, kind: 'city' }} alt={p.name} seed={p.name} className="w-full h-full group-hover:scale-105 transition-transform" />
                </div>
                <div className="p-4">
                  <h4 className="font-bold text-slate-900">{p.name}</h4>
                  <p className="text-xs text-slate-500">{p.state} · {p.tagline}</p>
                  <p className="text-sm font-bold text-primary mt-2">from {formatINR(p.avg_daily)}/day <span className="text-[10px] font-medium text-slate-400">approx.</span></p>
                </div>
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
