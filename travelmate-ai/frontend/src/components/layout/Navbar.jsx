import { useState } from 'react';
import { Search, Plus, LogOut, Menu } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const TITLES = [
  ['/dashboard', 'Dashboard', 'Your journeys, budget and AI insights'],
  ['/trips', 'My Trips', 'Everything you have planned'],
  ['/planner', 'AI Trip Planner', 'Tell us what you like — we plan the rest'],
  ['/explore', 'Explore', 'Handpicked destinations around the world'],
  ['/hotels', 'Hotels', 'Find a place to stay'],
  ['/flights', 'Flights', 'Compare routes and fares'],
  ['/budget', 'Budget', 'Estimated vs. actual spending'],
  ['/assistant', 'AI Assistant', 'Ask anything about your trip'],
  ['/saved', 'Saved Places', 'Your shortlist'],
  ['/settings', 'Settings', 'Your account'],
];

export default function Navbar({ onMenu = () => {} }) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [q, setQ] = useState('');

  const [, title, subtitle] = TITLES.find(([p]) => pathname === p || pathname.startsWith(p + '/')) || ['', 'TravelMate AI', ''];

  const search = (e) => {
    e.preventDefault();
    const term = q.trim();
    if (term) navigate(`/explore?q=${encodeURIComponent(term)}`);
  };

  return (
    <header className="h-16 sm:h-20 bg-surface/80 backdrop-blur-md flex items-center justify-between gap-3 px-4 sm:px-8 sticky top-0 z-30 border-b border-slate-200/50">
      <div className="flex items-center gap-3 min-w-0">
        <button onClick={onMenu} className="lg:hidden w-10 h-10 bg-white border border-slate-200 rounded-xl flex items-center justify-center text-slate-600" aria-label="Open menu">
          <Menu size={18} />
        </button>
        <div className="min-w-0">
          <h2 className="text-lg sm:text-xl font-bold text-slate-800 truncate">{title}</h2>
          <p className="text-xs text-slate-500 truncate hidden sm:block">{subtitle}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <form onSubmit={search} className="relative hidden md:block" role="search">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            type="search"
            aria-label="Search destinations"
            placeholder="Search destinations, e.g. Paris"
            className="pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm w-64 lg:w-72 focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10"
          />
        </form>

        <span className="hidden lg:inline-flex px-3 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700" title="All prices are shown in Indian Rupees (converted from local prices)">₹ INR</span>

        <button onClick={() => navigate('/planner')} className="btn-primary px-3 sm:px-5">
          <Plus size={16} /> <span className="hidden sm:inline">New AI Trip</span>
        </button>

        <button onClick={logout} className="w-10 h-10 bg-white border border-slate-200 rounded-xl flex items-center justify-center text-slate-500 hover:bg-red-50 hover:text-red-500" title="Log out" aria-label="Log out">
          <LogOut size={16} />
        </button>
      </div>
    </header>
  );
}
