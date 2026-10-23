import { Footprints, Car, Bus, TrainFront, Ship, CarTaxiFront } from 'lucide-react';
import { formatINR } from '../utils/formatters';

const ICONS = { Walk: Footprints, Auto: CarTaxiFront, Cab: Car, Metro: TrainFront, Bus, Train: TrainFront, Ferry: Ship };
const LABEL = { Auto: 'Auto-rickshaw', Cab: 'Cab / taxi', Walk: 'Walk', Metro: 'Metro', Bus: 'Bus', Train: 'Train', Ferry: 'Ferry' };

// "How do we get from the previous stop to this one, and what does it cost?"
export default function TravelConnector({ travel, fromStay = false }) {
  if (!travel || (!travel.distance_km && !travel.cost_inr)) return null;
  const Icon = ICONS[travel.mode] || Car;
  return (
    <div className="flex items-center gap-3 pl-5 py-1.5" aria-label="Travel to the next stop">
      <div className="w-px self-stretch border-l-2 border-dashed border-secondary/40 -my-1.5" aria-hidden="true" />
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 bg-orange-50 border border-orange-100 rounded-full pl-1.5 pr-4 py-1">
        <span className="w-7 h-7 rounded-full bg-secondary text-white flex items-center justify-center"><Icon size={14} /></span>
        <span className="text-xs font-extrabold text-primary">{LABEL[travel.mode] || travel.mode}</span>
        {travel.distance_km > 0 && <span className="text-xs font-semibold text-slate-600">{travel.distance_km} km</span>}
        {travel.duration_minutes > 0 && <span className="text-xs font-semibold text-slate-600">{travel.duration_minutes} min</span>}
        <span className="text-xs font-extrabold text-secondary">{travel.cost_inr > 0 ? `≈ ${formatINR(travel.cost_inr)}` : 'Free'}</span>
        {fromStay && <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400">from your stay</span>}
      </div>
    </div>
  );
}
