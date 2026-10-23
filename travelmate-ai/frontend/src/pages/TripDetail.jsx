import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { RefreshCw, Download, Calendar, Users, Wallet, Plane, Hotel as HotelIcon, Loader2, Sparkles, AlertTriangle, ExternalLink, Landmark } from "lucide-react";
import api from "../api/axios";
import Loader from "../components/ui/Loader";
import DaySection from "../components/DaySection";
import MapView from "../components/MapView";
import WeatherCard from "../components/WeatherCard";
import BudgetChart from "../components/BudgetChart";
import RestaurantCard from "../components/RestaurantCard";
import CoverImage from "../components/ui/CoverImage";
import GettingThere from "../components/GettingThere";
import { useImage } from "../hooks/useImage";
import { useToast } from "../context/ToastContext";
import { getErrorMessage } from "../utils/errors";
import { cityToIata } from "../utils/constants";
import { formatDate, formatINR } from "../utils/formatters";

export default function TripDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [trip, setTrip] = useState(null);
  const [itinerary, setItinerary] = useState(null);
  const [budget, setBudget] = useState(null);
  const [hotels, setHotels] = useState([]);
  const [restaurants, setRestaurants] = useState([]);
  const [attractions, setAttractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const hero = useImage(trip ? { q: trip.destination, kind: "city" } : null, !!trip);

  const loadBudget = useCallback(() => {
    api.get(`/trips/${id}/budget`).then((r) => setBudget(r.data)).catch(() => setBudget(null));
  }, [id]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true); setNotFound(false);
    Promise.all([
      api.get(`/trips/${id}`),
      api.get(`/trips/${id}/itinerary`).then((r) => r.data).catch(() => null),
    ]).then(([t, it]) => {
      if (cancelled) return;
      const tr = t.data;
      setTrip(tr); setItinerary(it);
      loadBudget();
      const params = { city: tr.destination };
      api.get('/hotels/search', { params: { ...params, check_in: tr.start_date || undefined, check_out: tr.end_date || undefined, adults: tr.travelers } })
        .then((h) => !cancelled && setHotels(h.data.slice(0, 3))).catch(() => {});
      api.get('/places/restaurants', { params: { ...params, limit: 3 } }).then((r) => !cancelled && setRestaurants(r.data.slice(0, 3))).catch(() => {});
      api.get('/places/attractions', { params: { ...params, limit: 5 } }).then((r) => !cancelled && setAttractions(r.data.slice(0, 5))).catch(() => {});
    }).catch((err) => { if (!cancelled && err.response?.status === 404) setNotFound(true); else if (!cancelled) addToast(getErrorMessage(err, 'Could not load this trip'), 'error'); })
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, [id, loadBudget, addToast]);

  const generate = async () => {
    setBusy(true);
    try {
      const { data } = await api.post(`/trips/${id}/generate`, null, { timeout: 120000 });
      setItinerary(data);
      setTrip((t) => ({ ...t, status: 'generated' }));
      loadBudget();
      addToast('Itinerary updated');
    } catch (err) { addToast(getErrorMessage(err, 'Generation failed'), 'error'); }
    finally { setBusy(false); }
  };

  const downloadPdf = async () => {
    setExporting(true);
    try {
      const res = await api.get(`/trips/${id}/export/pdf`, { responseType: 'blob', timeout: 60000 });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url; a.download = `travelmate-${trip.destination.replace(/\W+/g, '-').toLowerCase()}.pdf`;
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      // blob error bodies are not JSON-parsed by axios, so use a generic message
      addToast(err.response?.status === 400 ? 'Generate the itinerary first' : 'Could not create the PDF', 'error');
    } finally { setExporting(false); }
  };

  if (loading) return <Loader text="Loading trip..." />;
  if (notFound || !trip) {
    return (
      <div className="page"><div className="glass-panel p-10 text-center">
        <p className="text-slate-600 mb-4">This trip doesn’t exist or isn’t yours.</p>
        <button className="btn-primary" onClick={() => navigate('/trips')}>Back to My Trips</button>
      </div></div>
    );
  }

  const from = cityToIata(trip.departure);
  const to = cityToIata(trip.destination);
  const flightQuery = new URLSearchParams({ ...(from && { from }), ...(to && { to }), ...(trip.start_date && { date: trip.start_date }) }).toString();
  const breakdown = budget ? Object.entries(budget.by_category_inr || {}).map(([category, amount]) => ({ category, amount })) : [];

  return (
    <div className="page">
      <div className="bg-primary rounded-3xl p-6 sm:p-8 pt-24 sm:pt-32 relative overflow-hidden mb-6 shadow-float flex flex-col md:flex-row md:justify-between md:items-end gap-5">
        {hero.url && <img src={hero.url} alt="" referrerPolicy="no-referrer" className="absolute inset-0 w-full h-full object-cover" />}
        <div className={`absolute inset-0 ${hero.url ? "bg-gradient-to-t from-primary via-primary/70 to-primary/20" : "bg-transparent"}`} aria-hidden="true" />
        {!hero.url && <div className="absolute -right-10 -top-10 w-56 h-56 rounded-full bg-secondary/20 blur-3xl" aria-hidden="true" />}
        <div className="relative z-10">
          <div className="flex items-center gap-2 text-xs font-bold text-secondary uppercase tracking-wider mb-2">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" /> {trip.trip_type} trip{trip.status === 'draft' ? ' · draft' : ''}
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white leading-tight capitalize drop-shadow">{trip.destination}</h1>
          <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4 text-sm font-semibold text-indigo-200">
            <span className="flex items-center gap-2"><Calendar className="w-4 h-4" /> {trip.start_date ? `${formatDate(trip.start_date)} – ${formatDate(trip.end_date)}` : 'Dates not set'}</span>
            <span className="flex items-center gap-2"><Users className="w-4 h-4" /> {trip.travelers} traveller{trip.travelers > 1 ? 's' : ''}</span>
            {trip.budget > 0 && <span className="flex items-center gap-2"><Wallet className="w-4 h-4" /> {formatINR(trip.budget)}</span>}
          </div>
        </div>
        <div className="relative z-10 flex flex-wrap gap-3">
          <button onClick={generate} disabled={busy} className="bg-white/10 text-white font-bold px-4 py-2.5 rounded-xl text-sm hover:bg-white/20 transition-all flex items-center gap-2 disabled:opacity-60">
            <RefreshCw className={`w-4 h-4 ${busy ? 'animate-spin' : ''}`} /> {itinerary ? 'AI Re-Optimize' : 'Generate itinerary'}
          </button>
          {itinerary && (
            <button onClick={downloadPdf} disabled={exporting} className="bg-secondary text-white font-bold px-4 py-2.5 rounded-xl text-sm hover:bg-orange-600 transition-all flex items-center gap-2 disabled:opacity-60">
              {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />} PDF
            </button>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6 lg:gap-8">
        <div className="lg:col-span-2 space-y-6 min-w-0">
          {itinerary?.source === 'demo' && (
            <div className="flex gap-3 items-start bg-amber-50 border border-amber-200 text-amber-800 rounded-2xl p-4 text-sm">
              <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p><b>Sample itinerary.</b> This plan comes from built-in sample data, not the live AI.</p>
                {itinerary.ai_error
                  ? <p className="mt-1">Why: <code className="break-words">{itinerary.ai_error}</code></p>
                  : <p className="mt-1">No Gemini key is active. Add one in <code>backend/.env</code> for a personalised plan.</p>}
                <p className="mt-1 text-xs">Check the connection in <Link to="/settings" className="underline font-semibold">Settings → Test Gemini</Link>, then use AI Re-Optimize.</p>
              </div>
            </div>
          )}

          {!busy && <GettingThere info={itinerary?.getting_there} />}

          {busy ? (
            <div className="glass-panel p-12 text-center"><Loader2 className="w-10 h-10 animate-spin mx-auto text-secondary" /><p className="text-sm text-slate-500 mt-3">Planning your days…</p></div>
          ) : itinerary?.days?.length ? (
            itinerary.days.map((day) => <DaySection key={day.day_number} day={day} destination={trip.destination} />)
          ) : (
            <div className="glass-panel p-10 text-center">
              <Sparkles className="w-8 h-8 text-secondary mx-auto mb-3" />
              <p className="text-slate-600 mb-4">No itinerary yet. Let the AI plan your days.</p>
              <button className="btn-primary" onClick={generate}>Generate itinerary</button>
            </div>
          )}

          {itinerary && (itinerary.assumptions?.length > 0 || itinerary.warnings?.length > 0) && !busy && (
            <div className="glass-panel p-5 text-sm text-slate-600 space-y-3">
              {itinerary.warnings?.filter((w) => itinerary.source !== 'demo' || !/sample/i.test(w)).length > 0 && (
                <div><h4 className="font-bold text-amber-700 mb-1">Heads up</h4><ul className="list-disc pl-5 space-y-0.5">{itinerary.warnings.filter((w) => itinerary.source !== 'demo' || !/sample/i.test(w)).map((w, i) => <li key={i}>{w}</li>)}</ul></div>
              )}
              {itinerary.assumptions?.length > 0 && (
                <div><h4 className="font-bold text-primary mb-1">Assumptions</h4><ul className="list-disc pl-5 space-y-0.5">{itinerary.assumptions.map((a, i) => <li key={i}>{a}</li>)}</ul></div>
              )}
            </div>
          )}

          <div className="glass-panel p-4">
            <h3 className="font-bold text-primary mb-3 px-1">Map</h3>
            <MapView destination={trip.destination} origin={trip.departure} />
          </div>
        </div>

        <div className="space-y-6 min-w-0">
          <WeatherCard city={trip.destination} />

          {budget && (itinerary || budget.spent_inr > 0) && (
            <div>
              <BudgetChart breakdown={breakdown} budget={trip.budget} label="AI estimate" />
              {budget.spent_inr > 0 && <p className="text-xs text-slate-500 mt-2 px-1">Logged so far: <b>{formatINR(budget.spent_inr)}</b> · <Link to="/budget" className="text-secondary font-semibold">Manage expenses</Link></p>}
            </div>
          )}

          <div className="glass-panel p-5">
            <h3 className="font-bold text-primary mb-4 flex items-center gap-2"><HotelIcon className="w-4 h-4 text-secondary" /> Stays nearby</h3>
            {hotels.length === 0 ? <p className="text-sm text-slate-500">No stays found.</p> : (
              <div className="space-y-4">
                {hotels.map((h) => (
                  <div key={h.id} className="flex gap-3 items-center border-b border-slate-50 pb-4 last:border-0 last:pb-0">
                    <CoverImage src={h.image} lookup={{ q: h.name, kind: "hotel", city: trip.destination }} alt={h.name} seed={h.name} icon={HotelIcon} className="w-16 h-16 rounded-xl shrink-0" showTag={false} />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-extrabold text-primary truncate">{h.name}</div>
                      <div className="text-[11px] text-slate-500 truncate">{h.address}</div>
                    </div>
                    <a href={h.booking_link} target="_blank" rel="noopener noreferrer" className="text-[10px] font-bold bg-slate-100 px-3 py-1.5 rounded-lg hover:bg-slate-200 transition-colors inline-flex items-center gap-1 shrink-0">Price <ExternalLink className="w-3 h-3" /></a>
                  </div>
                ))}
              </div>
            )}
            <Link to={`/hotels?city=${encodeURIComponent(trip.destination)}${trip.start_date ? `&check_in=${trip.start_date}` : ''}${trip.end_date ? `&check_out=${trip.end_date}` : ''}`} className="block mt-4 text-xs font-semibold text-secondary">See all hotels →</Link>
          </div>

          <div className="glass-panel p-5">
            <h3 className="font-bold text-primary mb-3 flex items-center gap-2"><Plane className="w-4 h-4 text-secondary" /> Flights</h3>
            <div className="bg-slate-50 p-4 rounded-xl">
              <div className="flex justify-between items-center">
                <div className="font-bold text-primary text-lg">{from || '—'}</div>
                <div className="text-xs text-slate-400">→</div>
                <div className="font-bold text-primary text-lg">{to || '—'}</div>
              </div>
              <Link to={`/flights${flightQuery ? `?${flightQuery}` : ''}`} className="w-full btn-secondary mt-3 text-xs py-2">Search flights</Link>
              {(!from || !to) && <p className="text-[11px] text-slate-500 mt-2">Couldn’t match one of the cities to an airport — enter the codes on the next page.</p>}
            </div>
          </div>

          {attractions.length > 0 && (
            <div className="glass-panel p-5">
              <h3 className="font-bold text-primary mb-3 flex items-center gap-2"><Landmark className="w-4 h-4 text-secondary" /> Places worth a look</h3>
              <ul className="space-y-3">
                {attractions.map((a) => (
                  <li key={a.id} className="flex items-center gap-3">
                    <CoverImage lookup={{ q: a.name, kind: "place", exclude: trip.destination }} alt={a.name} seed={a.name} icon={Landmark} className="w-16 h-16 rounded-xl shrink-0" showTag={false} />
                    <div className="min-w-0"><div className="text-sm font-extrabold text-primary truncate">{a.name}</div><div className="text-xs font-semibold text-slate-500">{a.category}</div></div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {restaurants.length > 0 && (
            <div>
              <h3 className="font-bold text-primary mb-3 px-1">Where to eat</h3>
              <div className="space-y-3">{restaurants.map((r, i) => <RestaurantCard key={r.id} restaurant={r} index={i} />)}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
