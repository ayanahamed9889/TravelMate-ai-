import { LayoutDashboard, Map, Plane, Hotel, Sparkles, Settings, Bookmark, Compass, Bot, Wallet, X } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const navItems = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { name: 'My Trips', icon: Map, path: '/trips' },
  { name: 'AI Trip Planner', icon: Sparkles, path: '/planner', badge: 'NEW' },
  { name: 'Explore Destinations', icon: Compass, path: '/explore' },
  { name: 'Hotels Search', icon: Hotel, path: '/hotels' },
  { name: 'Flights Search', icon: Plane, path: '/flights' },
  { name: 'Budget', icon: Wallet, path: '/budget' },
  { name: 'AI Assistant', icon: Bot, path: '/assistant' },
  { name: 'Saved Places', icon: Bookmark, path: '/saved' },
  { name: 'Settings', icon: Settings, path: '/settings' },
];

export default function Sidebar({ open = false, onClose = () => {} }) {
  const { user } = useAuth();
  const initial = (user?.name || user?.email || 'T').trim().charAt(0).toUpperCase();

  return (
    <>
      {open && <div className="fixed inset-0 bg-slate-900/40 z-40 lg:hidden" onClick={onClose} aria-hidden="true" />}
      <aside
        className={`w-64 h-screen fixed left-0 top-0 bg-surface border-r border-slate-200 flex flex-col p-4 z-50 transition-transform duration-200 lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}
        aria-label="Main navigation"
      >
        <div className="flex items-center justify-between mb-8 px-2 mt-4">
          <div className="flex items-center gap-2">
            <img src="/logo.svg" alt="" className="w-9 h-9" />
            <div>
              <h1 className="font-bold text-lg leading-tight text-primary">TravelMate</h1>
              <p className="text-[10px] text-secondary font-bold tracking-wider">AI INTELLIGENCE</p>
            </div>
          </div>
          <button onClick={onClose} className="lg:hidden p-1.5 rounded-lg hover:bg-slate-100" aria-label="Close menu"><X size={18} /></button>
        </div>

        <nav className="flex-1 overflow-y-auto space-y-1">
          <p className="text-xs font-bold text-slate-400 mb-3 px-2 tracking-wider">NAVIGATION</p>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${isActive ? 'bg-primary text-white shadow-md' : 'text-slate-600 hover:bg-slate-100'}`}
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <item.icon size={18} className={isActive ? 'text-white' : 'text-slate-400'} />
                    {item.name}
                  </div>
                  {item.badge && (
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${isActive ? 'bg-secondary text-white' : 'bg-orange-100 text-secondary'}`}>{item.badge}</span>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mt-4 p-2 bg-white rounded-xl border border-slate-100 shadow-sm flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm shrink-0">{initial}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-slate-800 truncate">{user?.name || 'Traveler'}</p>
            <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
          </div>
        </div>
      </aside>
    </>
  );
}
