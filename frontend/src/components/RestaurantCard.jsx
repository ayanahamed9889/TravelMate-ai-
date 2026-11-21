import { motion } from "framer-motion";
import { MapPin, Star, Utensils } from "lucide-react";

export default function RestaurantCard({ restaurant, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index, 8) * 0.04 }}
      className="bg-white rounded-2xl p-3.5 border border-slate-100 shadow-glass flex gap-3"
    >
      <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center shrink-0">
        <Utensils className="w-6 h-6 text-secondary" />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-bold text-primary text-sm line-clamp-1">{restaurant.name}</h3>
        <div className="flex items-center gap-2 mt-0.5 text-xs">
          {restaurant.rating > 0 && (
            <span className="flex items-center gap-1 text-amber-600 font-semibold">
              <Star className="w-3 h-3 fill-current" />{Number(restaurant.rating).toFixed(1)}
            </span>
          )}
          <span className="text-slate-500 line-clamp-1">{restaurant.category}</span>
        </div>
        {restaurant.description && (
          <div className="flex items-center gap-1 mt-1 text-xs text-slate-500">
            <MapPin className="w-3 h-3 shrink-0" />
            <span className="line-clamp-1">{restaurant.description}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
