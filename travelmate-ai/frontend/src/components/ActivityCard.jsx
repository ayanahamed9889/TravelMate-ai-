import { Clock, MapPin, Utensils, Landmark, Mountain, ShoppingBag, Bed, Bus, Sparkles, Palmtree } from "lucide-react";
import { formatINR } from "../utils/formatters.js";
import CoverImage from "./ui/CoverImage";

const ICONS = [
  [/food|restaurant|dining|cafe|meal/i, Utensils],
  [/history|culture|heritage|museum|temple/i, Landmark],
  [/nature|adventure|trek|park/i, Mountain],
  [/shop|market/i, ShoppingBag],
  [/stay|hotel|accommodation/i, Bed],
  [/transit|transport|travel/i, Bus],
  [/relax|spa|beach/i, Palmtree],
];
const iconFor = (cat) => (ICONS.find(([re]) => re.test(cat || "")) || [null, Sparkles])[1];

// Meals, hotel check-ins and transfers have no landmark photo, so no lookup is attempted for them
const NO_PHOTO = /food|restaurant|dining|cafe|meal|stay|hotel|accommodation|transit|transport|travel|relax|spa|shop/i;

export default function ActivityCard({ activity, destination = "" }) {
  const Icon = iconFor(activity.category);
  const cost = Number(activity.estimated_cost_inr ?? activity.estimated_cost);
  const wantsPhoto = !NO_PHOTO.test(activity.category || "") && !!destination;

  return (
    <article className="flex flex-col sm:flex-row rounded-2xl bg-white border border-slate-200 shadow-glass overflow-hidden hover:shadow-md transition-shadow">
      <div className="sm:w-44 md:w-52 shrink-0 h-40 sm:h-auto sm:min-h-[150px]">
        <CoverImage
          lookup={wantsPhoto ? { q: activity.name, kind: "place", exclude: destination } : null}
          alt={activity.name} seed={activity.name} icon={Icon} className="w-full h-full" showTag={false}
        />
      </div>

      <div className="flex-1 min-w-0 p-4 sm:p-5">
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <span className="inline-flex items-center gap-1.5 bg-primary text-white text-xs font-extrabold px-3 py-1 rounded-full"><Clock className="w-3.5 h-3.5" />{activity.start_time}</span>
          {activity.category && <span className="text-[11px] font-extrabold uppercase tracking-wider text-secondary bg-orange-50 px-2.5 py-1 rounded-full">{activity.category}</span>}
          {Number.isFinite(cost) && (
            <span className="ml-auto text-base font-extrabold text-tertiary bg-emerald-50 px-3 py-1 rounded-full">{cost > 0 ? formatINR(cost) : "Free"}</span>
          )}
        </div>

        <h4 className="text-lg sm:text-xl font-extrabold text-primary leading-snug">{activity.name}</h4>
        {activity.description && <p className="text-sm sm:text-[15px] font-medium text-slate-700 mt-1.5 leading-relaxed">{activity.description}</p>}

        <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 mt-3 text-xs sm:text-sm font-semibold text-slate-600">
          {activity.duration_minutes > 0 && <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-secondary" />{activity.duration_minutes} min</span>}
          {activity.location && <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4 text-secondary" />{activity.location}</span>}
        </div>
        {activity.notes && <p className="text-sm font-medium text-amber-800 bg-amber-50 rounded-lg px-3 py-2 mt-3">💡 {activity.notes}</p>}
      </div>
    </article>
  );
}
