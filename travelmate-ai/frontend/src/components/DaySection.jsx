import ActivityCard from './ActivityCard';
import TravelConnector from './TravelConnector';
import { formatDate, formatINR } from '../utils/formatters';

const num = (x) => Number(x) || 0;

export default function DaySection({ day, destination = '' }) {
  const activities = day.activities || [];
  const spend = activities.reduce((s, a) => s + num(a.estimated_cost_inr ?? a.estimated_cost), 0);
  const travel = activities.reduce((s, a) => s + num(a.travel?.cost_inr), 0);
  const km = activities.reduce((s, a) => s + num(a.travel?.distance_km), 0);

  return (
    <section className="rounded-3xl overflow-hidden border border-slate-200 bg-white shadow-glass">
      <header className="bg-gradient-to-r from-primary to-indigo-800 text-white p-5 sm:p-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-secondary flex flex-col items-center justify-center shrink-0 leading-none">
            <span className="text-[10px] font-extrabold tracking-widest">DAY</span>
            <span className="text-2xl font-extrabold">{day.day_number}</span>
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-xl sm:text-2xl font-extrabold leading-snug">{day.theme || day.title || `Day ${day.day_number}`}</h3>
            {day.date && <p className="text-sm font-semibold text-indigo-200 mt-0.5">{formatDate(day.date)}</p>}
          </div>
        </div>
        {(spend > 0 || travel > 0) && (
          <div className="flex flex-wrap gap-2 mt-4 text-xs font-extrabold">
            <span className="bg-white/15 rounded-full px-3 py-1.5">Activities {formatINR(spend)}</span>
            <span className="bg-white/15 rounded-full px-3 py-1.5">Local travel {formatINR(travel)}{km > 0 ? ` · ${km.toFixed(1)} km` : ''}</span>
            <span className="bg-secondary rounded-full px-3 py-1.5">Day total {formatINR(spend + travel)}</span>
          </div>
        )}
      </header>

      <div className="p-4 sm:p-6">
        {activities.length === 0 ? <p className="text-sm text-slate-500">No activities for this day.</p> : activities.map((act, idx) => (
          <div key={idx}>
            <TravelConnector travel={act.travel} fromStay={idx === 0} />
            <ActivityCard activity={act} destination={destination} />
            {idx < activities.length - 1 && !activities[idx + 1].travel && <div className="h-3" />}
          </div>
        ))}
      </div>
    </section>
  );
}
