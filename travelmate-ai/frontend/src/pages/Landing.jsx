import { Link } from 'react-router-dom';
import { Sparkles, Wallet, Map, Plane } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const FEATURES = [
  { icon: Sparkles, title: 'AI itineraries', text: 'Day-by-day plans tailored to your budget, pace and interests.' },
  { icon: Wallet, title: 'Rupee budgets', text: 'See estimated costs per day and track what you actually spend.' },
  { icon: Map, title: 'Explore the world', text: 'Handpicked destinations from Ladakh to Paris to Bali, with daily cost guides and real photos.' },
  { icon: Plane, title: 'Hotels & flights', text: 'Search stays and flights in one place, and export your plan as PDF.' },
];

export default function Landing() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary via-indigo-900 to-slate-900 text-white flex flex-col">
      <header className="flex items-center justify-between px-4 sm:px-10 py-5">
        <div className="flex items-center gap-2">
          <img src="/logo.svg" alt="" className="w-9 h-9" />
          <span className="font-bold text-lg">TravelMate <span className="text-secondary">AI</span></span>
        </div>
        <Link to={user ? '/dashboard' : '/login'} className="text-sm font-semibold px-4 py-2 rounded-xl border border-white/30 hover:bg-white/10">
          {user ? 'Dashboard' : 'Sign In'}
        </Link>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center py-10">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 bg-white/10 px-4 py-1.5 rounded-full text-xs font-bold mb-6 border border-white/20"><Sparkles size={14} /> AI INTELLIGENCE</div>
          <h1 className="text-4xl sm:text-5xl font-extrabold mb-4 leading-tight">Plan your dream trip anywhere in the world</h1>
          <p className="text-slate-300 mb-8 max-w-xl mx-auto">AI-curated itineraries, travel costs in rupees and booking-ready plans for 70+ destinations and any city on Earth.</p>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link to={user ? '/planner' : '/register'} className="btn-primary px-6 py-3">{user ? 'Plan a Trip' : 'Get Started Free'}</Link>
            {!user && <Link to="/login" className="inline-flex items-center px-6 py-3 rounded-xl border border-white/30 hover:bg-white/10 font-semibold text-sm">Sign In</Link>}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl w-full mt-14 text-left">
          {FEATURES.map((f) => (
            <div key={f.title} className="bg-white/5 border border-white/10 rounded-2xl p-5">
              <div className="w-10 h-10 rounded-xl bg-secondary/20 text-secondary flex items-center justify-center mb-3"><f.icon size={20} /></div>
              <h3 className="font-bold mb-1">{f.title}</h3>
              <p className="text-sm text-slate-300">{f.text}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
