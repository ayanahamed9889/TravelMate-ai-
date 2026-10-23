import { useEffect, useState } from 'react';
import { Cloud, CloudSun, Sun, CloudRain, CloudSnow, CloudFog, CloudLightning, Droplets, Wind } from 'lucide-react';
import api from '../api/axios';

const ICONS = { sun: Sun, 'cloud-sun': CloudSun, cloud: Cloud, rain: CloudRain, snow: CloudSnow, fog: CloudFog, storm: CloudLightning };

export default function WeatherCard({ city }) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!city) { setLoading(false); return undefined; }
    let cancelled = false;
    setLoading(true);
    api.get('/weather/forecast', { params: { city } })
      .then((res) => !cancelled && setWeather(res.data))
      .catch(() => !cancelled && setWeather(null))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, [city]);

  if (loading) return <div className="glass-panel p-5 animate-pulse h-36" />;
  if (!weather) return <div className="glass-panel p-5 text-sm text-slate-500">Weather unavailable for {city}</div>;

  const Icon = ICONS[weather.icon] || Cloud;
  return (
    <div className="rounded-2xl p-5 bg-gradient-to-br from-primary to-indigo-800 text-white shadow-glass">
      <div className="flex justify-between items-start mb-3">
        <div>
          <p className="text-[10px] font-bold text-white/60 uppercase tracking-widest">Weather now</p>
          <h4 className="font-bold text-sm">{weather.city}</h4>
        </div>
        <Icon size={26} className="text-amber-300" />
      </div>
      <div className="text-4xl font-extrabold mb-1">{Math.round(weather.temp)}°C</div>
      <p className="text-xs text-white/70 mb-3">{weather.condition}</p>
      <div className="flex gap-4 text-[11px] text-white/70 border-t border-white/10 pt-3">
        <span className="flex items-center gap-1"><Droplets size={12} />{weather.humidity}%</span>
        <span className="flex items-center gap-1"><Wind size={12} />{weather.wind} km/h</span>
      </div>
    </div>
  );
}
