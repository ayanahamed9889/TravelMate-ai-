import { motion } from "framer-motion";
import { Plane, Clock, ExternalLink } from "lucide-react";
import { formatINR, formatTime, durationToHours } from "../utils/formatters.js";

const AIRLINE_NAMES = {
  "6E": "IndiGo", AI: "Air India", IX: "Air India Express", QP: "Akasa Air", SG: "SpiceJet",
  EK: "Emirates", QR: "Qatar Airways", EY: "Etihad", BA: "British Airways", LH: "Lufthansa",
  AF: "Air France", SQ: "Singapore Airlines", TK: "Turkish Airlines", KL: "KLM", TG: "Thai Airways",
  CX: "Cathay Pacific", JL: "Japan Airlines", NH: "ANA", QF: "Qantas", AA: "American Airlines",
  UA: "United", DL: "Delta", AC: "Air Canada", SV: "Saudia", MH: "Malaysia Airlines", VS: "Virgin Atlantic",
};

export default function FlightCard({ flight, index = 0, date = "" }) {
  const airlineName = AIRLINE_NAMES[flight.airline] || flight.airline;
  const sample = flight.source === "demo";
  const gf = `https://www.google.com/travel/flights?q=${encodeURIComponent(`Flights from ${flight.origin} to ${flight.destination}${date ? ` on ${date}` : ""}`)}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index, 8) * 0.04 }}
      className="bg-white rounded-2xl border border-slate-100 shadow-glass hover:shadow-md hover:-translate-y-0.5 transition-all p-4 sm:p-5"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3 sm:w-48 shrink-0">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-indigo-500 flex items-center justify-center">
            <Plane className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-bold text-primary text-sm">{airlineName}</div>
            <div className="text-xs text-slate-500">{flight.airline} {flight.flight_number || ""}</div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-1">
          <div className="text-center">
            <div className="text-lg sm:text-xl font-extrabold text-primary">{formatTime(flight.departure_time)}</div>
            <div className="text-xs text-slate-500 font-medium">{flight.origin}</div>
          </div>
          <div className="flex-1 flex flex-col items-center">
            <div className="text-[10px] text-slate-400 font-semibold">{durationToHours(flight.duration)}</div>
            <div className="relative w-full my-2">
              <div className="h-[2px] bg-gradient-to-r from-secondary/20 via-secondary to-secondary/20 rounded" />
              <Plane className="w-3 h-3 text-secondary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rotate-90 bg-white" />
            </div>
            <div className="text-[10px] text-slate-500 font-medium">
              {flight.stops === 0 ? "Non-stop" : `${flight.stops} stop${flight.stops > 1 ? "s" : ""}`}
            </div>
          </div>
          <div className="text-center">
            <div className="text-lg sm:text-xl font-extrabold text-primary">{formatTime(flight.arrival_time)}</div>
            <div className="text-xs text-slate-500 font-medium">{flight.destination}</div>
          </div>
        </div>

        <div className="sm:text-right shrink-0 flex sm:block items-end justify-between">
          <div>
            <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">{sample ? "sample fare" : "from"}</div>
            <div className="text-xl sm:text-2xl font-extrabold text-primary">{formatINR(flight.price_inr)}</div>
          </div>
          <a href={gf} target="_blank" rel="noopener noreferrer" className="sm:mt-2 inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-primary text-white font-semibold hover:bg-indigo-900 transition-colors">
            Check live <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {durationToHours(flight.duration)}</span>
        <span className="capitalize">{flight.cabin?.toLowerCase() || "economy"}</span>
        <span className={`font-semibold ${sample ? "text-amber-600" : "text-tertiary"}`}>{sample ? "Sample price" : "Live price"}</span>
      </div>
    </motion.div>
  );
}
