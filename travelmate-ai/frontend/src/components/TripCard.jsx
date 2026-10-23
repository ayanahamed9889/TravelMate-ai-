import { Calendar, MapPin, Users, ChevronRight, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { formatDate, formatINR, daysBetween, todayISO } from '../utils/formatters';
import CoverImage from './ui/CoverImage';

function statusOf(trip) {
  if (trip.status === 'draft') return { label: 'Draft', cls: 'bg-amber-500' };
  if (trip.end_date && trip.end_date < todayISO()) return { label: 'Completed', cls: 'bg-slate-500' };
  return { label: 'Itinerary ready', cls: 'bg-emerald-500' };
}

export default function TripCard({ trip, onDelete }) {
  const status = statusOf(trip);
  const days = daysBetween(trip.start_date, trip.end_date);
  const dates = trip.start_date
    ? `${formatDate(trip.start_date)}${trip.end_date ? ` – ${formatDate(trip.end_date)}` : ''}`
    : 'Dates not set';

  return (
    <Link to={`/trips/${trip.id}`} className="glass-panel flex flex-col md:flex-row overflow-hidden group hover:shadow-md transition-shadow">
      <div className="w-full md:w-2/5 relative h-40 md:h-auto md:min-h-[180px]">
        <CoverImage src={trip.cover_image} lookup={{ q: trip.destination, kind: 'city' }} alt={trip.destination} seed={trip.destination} className="w-full h-full group-hover:scale-105 transition-transform duration-500" />
        <div className="absolute top-4 left-4 flex gap-2">
          <span className="bg-primary text-white text-[10px] font-bold px-3 py-1.5 rounded-full uppercase">{trip.trip_type || 'Trip'}</span>
          <span className={`${status.cls} text-white text-[10px] font-bold px-3 py-1.5 rounded-full uppercase`}>{status.label}</span>
        </div>
      </div>
      <div className="w-full md:w-3/5 p-5 sm:p-6 flex flex-col justify-between">
        <div>
          {days > 0 && <p className="text-[10px] font-bold text-secondary uppercase tracking-wider mb-1">{days}-day itinerary</p>}
          <h3 className="text-xl font-bold text-slate-900 mb-3 capitalize">{trip.destination}</h3>
          <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-slate-600">
            <span className="flex items-center gap-1"><Calendar size={12} /> {dates}</span>
            <span className="flex items-center gap-1"><Users size={12} /> {trip.travelers} traveller{trip.travelers > 1 ? 's' : ''}</span>
            {trip.departure && <span className="flex items-center gap-1 capitalize"><MapPin size={12} /> from {trip.departure.trim()}</span>}
          </div>
        </div>
        <div className="flex justify-between items-end mt-4 pt-4 border-t border-slate-100">
          <div>
            <p className="text-[10px] text-slate-400 uppercase">Total budget</p>
            <p className="text-lg font-extrabold text-primary">{trip.budget > 0 ? formatINR(trip.budget) : '—'}</p>
          </div>
          <div className="flex items-center gap-2">
            {onDelete && (
              <button
                onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDelete(trip); }}
                className="p-2 rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-500"
                aria-label={`Delete trip to ${trip.destination}`}
              >
                <Trash2 size={16} />
              </button>
            )}
            <span className="btn-dark text-xs px-4 py-2">View Trip <ChevronRight size={14} /></span>
          </div>
        </div>
      </div>
    </Link>
  );
}
