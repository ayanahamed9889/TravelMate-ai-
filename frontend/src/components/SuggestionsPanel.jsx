import { Sparkles, MapPin, PiggyBank, Utensils, Bus, ShieldCheck, Backpack, Gem, CalendarDays, Stamp } from 'lucide-react';

const SECTIONS = [
  ['best_areas_to_stay', 'Best areas to stay', MapPin],
  ['money_saving', 'Save money', PiggyBank],
  ['food', 'Food to try', Utensils],
  ['transport', 'Getting around', Bus],
  ['safety', 'Stay safe', ShieldCheck],
  ['packing', 'Packing', Backpack],
  ['hidden_gems', 'Hidden gems', Gem],
];

// AI suggestions for the trip (or clearly-labelled general tips when the AI was not used).
export default function SuggestionsPanel({ suggestions }) {
  if (!suggestions) return null;
  const blocks = SECTIONS.filter(([key]) => suggestions[key]?.length > 0);
  if (!blocks.length && !suggestions.summary) return null;
  const ai = suggestions.source === 'ai';

  return (
    <section className="rounded-3xl bg-white border border-slate-200 shadow-glass overflow-hidden" aria-label="Suggestions">
      <header className="p-5 sm:p-6 bg-gradient-to-r from-secondary to-orange-600 text-white">
        <p className="text-[11px] font-extrabold uppercase tracking-widest text-white/80 flex items-center gap-1.5">
          <Sparkles size={13} /> {ai ? 'AI suggestions for your trip' : 'Travel tips for your trip'}
        </p>
        {suggestions.summary && <p className="text-sm sm:text-base font-semibold mt-2 leading-relaxed">{suggestions.summary}</p>}
        {!ai && <p className="text-xs text-white/80 mt-2">General tips - they are personalised once the live AI (Gemini) is connected.</p>}
      </header>

      <div className="p-4 sm:p-6 grid md:grid-cols-2 gap-4">
        {(suggestions.best_time || suggestions.visa) && (
          <div className="md:col-span-2 grid sm:grid-cols-2 gap-3">
            {suggestions.best_time && <p className="flex gap-2 text-sm font-medium text-slate-700 bg-slate-50 rounded-xl px-3 py-2.5"><CalendarDays size={16} className="shrink-0 mt-0.5 text-secondary" /> {suggestions.best_time}</p>}
            {suggestions.visa && <p className="flex gap-2 text-sm font-medium text-slate-700 bg-slate-50 rounded-xl px-3 py-2.5"><Stamp size={16} className="shrink-0 mt-0.5 text-secondary" /> {suggestions.visa}</p>}
          </div>
        )}
        {blocks.map(([key, title, Icon]) => (
          <div key={key} className="rounded-2xl border border-slate-200 p-4">
            <h4 className="flex items-center gap-2 text-sm font-extrabold text-primary mb-2"><Icon size={16} className="text-secondary" /> {title}</h4>
            <ul className="space-y-1.5 text-sm text-slate-700">
              {suggestions[key].map((t, i) => <li key={i} className="flex gap-2"><span className="text-secondary font-bold">•</span><span>{t}</span></li>)}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
