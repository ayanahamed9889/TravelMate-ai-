import { useEffect, useState } from 'react';
import { MapPin } from 'lucide-react';
import { useImage } from '../../hooks/useImage';

// Literal class names so Tailwind keeps them
const GRADIENTS = [
  'from-primary to-indigo-500',
  'from-secondary to-amber-400',
  'from-indigo-800 to-secondary',
  'from-slate-800 to-indigo-600',
  'from-orange-500 to-rose-500',
];

const hash = (s) => [...String(s)].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);

// Shows `src` if given, otherwise looks a photo up from `lookup` ({q, kind, exclude, city}).
// While loading, or when no matching photo exists, a gradient cover is drawn instead.
export default function CoverImage({ src, lookup, alt = '', seed = '', icon: Icon = MapPin, className = '', showTag = true }) {
  const found = useImage(lookup, !src && !!lookup);
  const url = src || found.url;
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [url]);

  if (!url || failed) {
    const g = GRADIENTS[hash(seed || alt) % GRADIENTS.length];
    return (
      <div role="img" aria-label={alt} className={`bg-gradient-to-br ${g} flex items-center justify-center ${found.loading ? 'animate-pulse' : ''} ${className}`}>
        <Icon className="w-9 h-9 text-white/80" />
      </div>
    );
  }
  return (
    <div className={`relative overflow-hidden ${className}`} title={found.credit || undefined}>
      <img src={url} alt={alt} loading="lazy" referrerPolicy="no-referrer" onError={() => setFailed(true)} className="w-full h-full object-cover" />
      {showTag && found.generic && (
        <span className="absolute bottom-2 left-2 text-[9px] font-bold uppercase tracking-wider bg-black/55 text-white px-2 py-0.5 rounded-full">Area photo</span>
      )}
    </div>
  );
}
