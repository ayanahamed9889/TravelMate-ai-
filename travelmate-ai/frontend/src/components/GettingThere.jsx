import { Plane, TrainFront, Bus, Car, ArrowRight } from 'lucide-react';
import { formatINR } from '../utils/formatters';

const ICONS = { Flight: Plane, Train: TrainFront, Bus, Car };

// Home city -> destination (round trip) estimate, counted in the trip budget
export default function GettingThere({ info }) {
  if (!info || !info.cost_inr) return null;
  const Icon = ICONS[info.mode] || Car;
  const h = Math.floor(info.duration_minutes / 60);
  const m = info.duration_minutes % 60;
  return (
    <section className="rounded-3xl bg-gradient-to-r from-secondary to-orange-600 text-white p-5 sm:p-6 shadow-glow">
      <p className="text-[11px] font-extrabold uppercase tracking-widest text-white/80 mb-2">Getting there · round trip</p>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <span className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center"><Icon size={24} /></span>
        <h3 className="text-xl sm:text-2xl font-extrabold flex items-center gap-2 flex-wrap">
          {info.from_place || 'Home'} <ArrowRight size={20} /> {info.to}
        </h3>
        <span className="ml-auto text-2xl sm:text-3xl font-extrabold">≈ {formatINR(info.cost_inr)}</span>
      </div>
      <div className="flex flex-wrap gap-2 mt-4 text-xs font-extrabold">
        <span className="bg-white/20 rounded-full px-3 py-1.5">{info.mode}</span>
        {info.distance_km > 0 && <span className="bg-white/20 rounded-full px-3 py-1.5">~{info.distance_km} km</span>}
        {info.duration_minutes > 0 && <span className="bg-white/20 rounded-full px-3 py-1.5">~{h}h {m}m one way</span>}
      </div>
      {info.note && <p className="text-sm font-medium text-white/90 mt-3">{info.note} This is an estimate for your whole group.</p>}
    </section>
  );
}
