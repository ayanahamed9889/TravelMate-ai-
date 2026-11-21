import { Bed, ExternalLink, MapPin, Sparkles } from 'lucide-react';
import { formatINR } from '../utils/formatters';

// Hotel / stay cost for the whole trip, three price levels, and the AI's hotel ideas.
export default function StayCard({ hotel, picks = [], destination = '' }) {
  if (!hotel) return null;
  const none = hotel.nights === 0;
  const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;

  return (
    <section className="rounded-3xl bg-white border border-slate-200 shadow-glass overflow-hidden" aria-label="Hotel cost">
      <header className="p-5 sm:p-6 bg-gradient-to-r from-indigo-50 to-orange-50 border-b border-slate-100">
        <p className="text-[11px] font-extrabold uppercase tracking-widest text-secondary mb-1">Where you stay</p>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          <span className="w-12 h-12 rounded-2xl bg-primary text-white flex items-center justify-center"><Bed size={22} /></span>
          <div className="min-w-0">
            <h3 className="text-xl font-extrabold text-primary capitalize">{hotel.accommodation} · {hotel.tier}</h3>
            <p className="text-sm font-semibold text-slate-600">
              {none ? 'No overnight stay' : `${plural(hotel.nights, 'night')} × ${plural(hotel.rooms, hotel.unit)} × ${formatINR(hotel.per_night_inr)}`}
            </p>
          </div>
          <span className="ml-auto text-2xl sm:text-3xl font-extrabold text-primary">{none ? '₹0' : `≈ ${formatINR(hotel.cost_inr)}`}</span>
        </div>
      </header>

      {!none && (
        <div className="p-4 sm:p-6 space-y-5">
          {hotel.options?.length > 0 && (
            <div>
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 mb-2">Compare stay levels</h4>
              <div className="grid sm:grid-cols-3 gap-3">
                {hotel.options.map((o) => (
                  <div key={o.tier} className={`rounded-2xl border p-3.5 ${o.selected ? 'border-secondary bg-orange-50/60' : 'border-slate-200'}`}>
                    <p className="text-sm font-extrabold text-primary capitalize">{o.label}</p>
                    <p className="text-lg font-extrabold text-slate-900 mt-1">{formatINR(o.total_inr)}</p>
                    <p className="text-xs font-medium text-slate-500">{formatINR(o.per_night_inr)} per {hotel.unit} / night</p>
                    {o.selected && <span className="inline-block mt-2 text-[10px] font-extrabold uppercase tracking-wider text-secondary">Your choice</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {hotel.cheaper_option && (
            <p className="text-sm font-medium text-emerald-800 bg-emerald-50 rounded-xl px-3 py-2.5">
              💰 A <b>{hotel.cheaper_option.label.toLowerCase()}</b> would cost about {formatINR(hotel.cheaper_option.total_inr)} - saves roughly {formatINR(hotel.cheaper_option.saving_inr)}.
            </p>
          )}

          {picks.length > 0 && (
            <div>
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5"><Sparkles size={13} className="text-secondary" /> AI hotel ideas · verify availability and price</h4>
              <ul className="space-y-2">
                {picks.map((p) => (
                  <li key={p.name} className="flex items-start gap-3 rounded-xl border border-slate-200 p-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-extrabold text-primary">{p.name}</p>
                      {p.area && <p className="text-xs font-semibold text-slate-500 flex items-center gap-1"><MapPin size={11} /> {p.area}</p>}
                      {p.why && <p className="text-xs text-slate-600 mt-1">{p.why}</p>}
                    </div>
                    {p.price_per_night_inr > 0 && <p className="text-sm font-extrabold text-slate-900 shrink-0">≈ {formatINR(p.price_per_night_inr)}<span className="block text-[10px] font-medium text-slate-400 text-right">/ night</span></p>}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-500 max-w-md">{hotel.note}</p>
            {hotel.booking_link && (
              <a href={hotel.booking_link} target="_blank" rel="noopener noreferrer" className="btn-primary text-xs px-4 py-2">
                See live prices for {destination || 'this trip'} <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
