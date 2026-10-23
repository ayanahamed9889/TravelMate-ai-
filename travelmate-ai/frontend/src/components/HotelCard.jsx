import { motion } from "framer-motion";
import { Star, MapPin, Wifi, ExternalLink, Phone, Bed } from "lucide-react";
import { formatINR } from "../utils/formatters.js";
import CoverImage from "./ui/CoverImage";

export default function HotelCard({ hotel, index = 0 }) {
  const sample = hotel.source === "demo" || hotel.source === "fallback";
  const hasPrice = Number(hotel.price_inr) > 0;
  const stars = Math.min(5, Number(hotel.stars) || 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index, 8) * 0.04 }}
      className="bg-white rounded-2xl overflow-hidden border border-slate-100 shadow-glass hover:-translate-y-0.5 hover:shadow-md transition-all flex flex-col"
    >
      <div className="relative h-48 overflow-hidden">
        <CoverImage src={hotel.image} lookup={{ q: hotel.name, kind: "hotel", city: hotel.city }} alt={hotel.name} seed={hotel.name} icon={Bed} className="w-full h-full" />
        {stars > 0 && (
          <div className="absolute top-3 left-3 px-2.5 py-1 rounded-lg bg-white/95 backdrop-blur flex items-center gap-0.5" aria-label={`${stars} star`}>
            {[...Array(stars)].map((_, i) => <Star key={i} className="w-3 h-3 fill-amber-400 text-amber-400" />)}
          </div>
        )}
        <div className={`absolute top-3 right-3 px-2 py-1 rounded-lg bg-white/95 backdrop-blur text-[10px] font-bold ${sample ? "text-amber-600" : "text-tertiary"}`}>
          {sample ? "SAMPLE" : "LIVE LISTING"}
        </div>
      </div>

      <div className="p-5 flex-1 flex flex-col">
        <h3 className="font-extrabold text-primary text-lg leading-snug line-clamp-2">{hotel.name}</h3>
        <div className="flex items-center gap-1 mt-2 text-xs text-slate-500">
          <MapPin className="w-3 h-3 shrink-0" />
          <span className="line-clamp-1">{hotel.address || hotel.location || hotel.city}</span>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {hotel.type && <span className="text-xs text-slate-600 bg-slate-50 px-2 py-1 rounded-lg">{hotel.type}</span>}
          <span className="inline-flex items-center gap-1 text-xs text-slate-600 bg-slate-50 px-2 py-1 rounded-lg"><Wifi className="w-3 h-3 text-secondary" /> Wifi</span>
          {hotel.phone && <span className="inline-flex items-center gap-1 text-xs text-slate-600 bg-slate-50 px-2 py-1 rounded-lg"><Phone className="w-3 h-3 text-secondary" />{hotel.phone}</span>}
        </div>

        <div className="mt-4 pt-4 border-t border-slate-100 flex items-end justify-between gap-3">
          <div>
            {hasPrice ? (
              <>
                <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
                  {hotel.nights ? `${hotel.nights} night${hotel.nights > 1 ? "s" : ""} total` : "From"}
                </div>
                <div className="text-xl font-extrabold text-primary">{formatINR(hotel.price_inr)}</div>
                {hotel.price_per_night_inr > 0 && hotel.nights > 1 && (
                  <div className="text-xs text-slate-500">{formatINR(hotel.price_per_night_inr)} / night</div>
                )}
              </>
            ) : (
              <div className="text-sm font-semibold text-slate-500">Price on Booking.com</div>
            )}
          </div>
          {hotel.booking_link && (
            <a href={hotel.booking_link} target="_blank" rel="noopener noreferrer" className="btn-primary text-xs px-3.5 py-2 whitespace-nowrap">
              {hasPrice ? "Book" : "Check price"} <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>
    </motion.div>
  );
}
