import { Link } from 'react-router-dom';
import { Plane, Hotel, Bus, Utensils, Ticket, ShoppingBag, Wallet, CheckCircle2, AlertTriangle, Lightbulb } from 'lucide-react';
import { formatINR } from '../utils/formatters';

const ICONS = {
  'Getting there': Plane, Stays: Hotel, Transit: Bus, Food: Utensils,
  Experiences: Ticket, Shopping: ShoppingBag, Other: Wallet,
};
const BARS = {
  'Getting there': 'bg-rose-400', Stays: 'bg-primary', Transit: 'bg-secondary', Food: 'bg-amber-400',
  Experiences: 'bg-tertiary', Shopping: 'bg-indigo-400', Other: 'bg-slate-400',
};
const STATUS = {
  within: { label: 'Within budget', cls: 'bg-emerald-100 text-emerald-700', Icon: CheckCircle2 },
  tight: { label: 'Tight budget', cls: 'bg-amber-100 text-amber-700', Icon: AlertTriangle },
  over: { label: 'Over budget', cls: 'bg-red-100 text-red-700', Icon: AlertTriangle },
};

// Everything the trip costs in one place: flights, hotel, local travel, food, sightseeing.
export default function CostSummary({ summary, travelers = 1, spent = 0 }) {
  if (!summary || !summary.items?.length) return null;
  const st = STATUS[summary.status];
  const budget = Number(summary.budget_inr) || 0;
  const pct = budget > 0 ? Math.round((summary.subtotal_inr / budget) * 100) : null;

  return (
    <section className="rounded-3xl bg-white border border-slate-200 shadow-glass overflow-hidden" aria-label="Trip cost summary">
      <header className="bg-gradient-to-r from-primary to-indigo-800 text-white p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[11px] font-extrabold uppercase tracking-widest text-indigo-200">Trip cost summary · whole group</p>
            <p className="text-3xl sm:text-4xl font-extrabold mt-1">{formatINR(summary.subtotal_inr)}</p>
            <p className="text-sm font-semibold text-indigo-200 mt-1">
              {formatINR(summary.per_person_inr)} per person · {formatINR(summary.per_day_inr)} per day · {travelers} traveller{travelers > 1 ? 's' : ''}
            </p>
          </div>
          {st && (
            <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-extrabold ${st.cls}`}>
              <st.Icon size={14} /> {st.label}
            </span>
          )}
        </div>
        {pct !== null && (
          <div className="mt-4">
            <div className="h-2 rounded-full bg-white/20 overflow-hidden" aria-hidden="true">
              <div className={`h-full ${pct > 100 ? 'bg-red-400' : pct > 85 ? 'bg-amber-400' : 'bg-emerald-400'}`} style={{ width: `${Math.min(pct, 100)}%` }} />
            </div>
            <p className="text-xs font-semibold text-indigo-200 mt-1.5">{pct}% of your {formatINR(budget)} budget</p>
          </div>
        )}
      </header>

      <div className="p-4 sm:p-6">
        <div className="h-2.5 w-full rounded-full flex overflow-hidden mb-5" aria-hidden="true">
          {summary.items.filter((i) => i.amount > 0).map((i) => (
            <div key={i.key} className={`${BARS[i.key] || 'bg-slate-400'} h-full`} style={{ width: `${i.percent}%` }} />
          ))}
        </div>

        <ul className="divide-y divide-slate-100">
          {summary.items.map((i) => {
            const Icon = ICONS[i.key] || Wallet;
            return (
              <li key={i.key} className="flex items-start gap-3 py-3">
                <span className={`w-9 h-9 shrink-0 rounded-xl flex items-center justify-center text-white ${BARS[i.key] || 'bg-slate-400'}`}><Icon size={17} /></span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-extrabold text-primary">{i.label}</p>
                  {i.detail && <p className="text-xs font-medium text-slate-500 mt-0.5">{i.detail}</p>}
                </div>
                <div className="text-right shrink-0">
                  <p className="text-base font-extrabold text-slate-900">{i.amount > 0 ? formatINR(i.amount) : '—'}</p>
                  {i.amount > 0 && <p className="text-[11px] font-semibold text-slate-400">{Math.round(i.percent)}%</p>}
                </div>
              </li>
            );
          })}
        </ul>

        <dl className="mt-3 pt-3 border-t border-slate-200 space-y-1.5 text-sm">
          <div className="flex justify-between"><dt className="font-semibold text-slate-600">Safety buffer (10%)</dt><dd className="font-bold text-slate-700">{formatINR(summary.buffer_inr)}</dd></div>
          <div className="flex justify-between text-base"><dt className="font-extrabold text-primary">Total with buffer</dt><dd className="font-extrabold text-primary">{formatINR(summary.total_with_buffer_inr)}</dd></div>
          {budget > 0 && (
            <div className="flex justify-between"><dt className="font-semibold text-slate-600">{summary.remaining_inr >= 0 ? 'Left from your budget' : 'Over your budget by'}</dt>
              <dd className={`font-bold ${summary.remaining_inr >= 0 ? 'text-tertiary' : 'text-red-600'}`}>{formatINR(Math.abs(summary.remaining_inr))}</dd></div>
          )}
        </dl>

        {summary.advice?.length > 0 && (
          <ul className="mt-4 space-y-2">
            {summary.advice.map((a, idx) => (
              <li key={idx} className="flex gap-2 text-sm font-medium text-amber-900 bg-amber-50 rounded-xl px-3 py-2.5">
                <Lightbulb size={16} className="shrink-0 mt-0.5 text-amber-600" /> <span>{a}</span>
              </li>
            ))}
          </ul>
        )}

        <p className="text-xs text-slate-500 mt-4">
          Planning estimates, not quotes - check live prices before booking.
          {spent > 0 && <> Logged so far: <b>{formatINR(spent)}</b> · <Link to="/budget" className="text-secondary font-semibold">Manage expenses</Link></>}
        </p>
      </div>
    </section>
  );
}
