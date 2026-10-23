import { formatINR } from '../utils/formatters';

const COLORS = {
  Stays: 'bg-primary',
  Transit: 'bg-secondary',
  Food: 'bg-amber-400',
  Experiences: 'bg-tertiary',
  Shopping: 'bg-indigo-400',
  Other: 'bg-slate-400',
  Misc: 'bg-slate-400',
};

// breakdown: [{category, amount}] · budget: optional total budget to compare against
export default function BudgetChart({ breakdown = [], budget = 0, label = 'Estimated total' }) {
  const items = breakdown.filter((i) => Number(i.amount) > 0);
  const total = items.reduce((s, i) => s + Number(i.amount), 0);
  const pct = budget > 0 ? Math.round((total / budget) * 100) : null;
  const over = pct !== null && pct > 100;

  if (total === 0) {
    return (
      <div className="glass-panel p-5 text-sm text-slate-500">
        No cost data yet. Generate an itinerary or log an expense to see the breakdown.
      </div>
    );
  }

  return (
    <div className="glass-panel p-5">
      <div className="flex justify-between items-end mb-4 gap-3">
        <div>
          <h3 className="text-2xl font-extrabold text-slate-900">{formatINR(total)}</h3>
          <p className="text-[11px] text-slate-500 uppercase font-bold">{label}</p>
        </div>
        {pct !== null && (
          <div className="text-right">
            <p className={`text-sm font-extrabold ${over ? 'text-red-600' : 'text-tertiary'}`}>{pct}% of budget</p>
            <p className="text-[11px] text-slate-500">of {formatINR(budget)}</p>
          </div>
        )}
      </div>

      {pct !== null && (
        <div className="h-1.5 w-full rounded-full bg-slate-100 mb-4 overflow-hidden" aria-hidden="true">
          <div className={`h-full ${over ? 'bg-red-500' : pct > 85 ? 'bg-amber-500' : 'bg-tertiary'}`} style={{ width: `${Math.min(pct, 100)}%` }} />
        </div>
      )}

      <div className="h-2 w-full rounded-full flex overflow-hidden mb-3">
        {items.map((item) => (
          <div key={item.category} className={`${COLORS[item.category] || 'bg-slate-400'} h-full`} style={{ width: `${(item.amount / total) * 100}%` }} />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-[11px] text-slate-600 font-medium">
        {items.map((item) => (
          <span key={item.category} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${COLORS[item.category] || 'bg-slate-400'}`} />
            {item.category} · {formatINR(item.amount)} ({Math.round((item.amount / total) * 100)}%)
          </span>
        ))}
      </div>
    </div>
  );
}
