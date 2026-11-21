// INR formatting — Indian digit grouping (₹1,23,456)
export const formatINR = (amount) => {
  const n = Number(amount);
  if (!Number.isFinite(n)) return "₹0";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n);
};

// Short form: ₹1.2L, ₹15K, ₹1.5Cr
export const formatINRShort = (amount) => {
  const n = Number(amount);
  if (!Number.isFinite(n) || n <= 0) return "₹0";
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  if (n >= 1000) return `₹${(n / 1000).toFixed(1)}K`;
  return `₹${Math.round(n)}`;
};

// Parse "YYYY-MM-DD" as a *local* date (new Date("2026-10-15") is UTC and can show the previous day)
export const parseLocalDate = (value) => {
  if (!value) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(value));
  const d = m ? new Date(+m[1], +m[2] - 1, +m[3]) : new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
};

export const formatDate = (value) => {
  const d = parseLocalDate(value);
  return d ? d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : "";
};

export const formatTime = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
};

export const daysBetween = (start, end) => {
  const s = parseLocalDate(start);
  const e = parseLocalDate(end);
  if (!s || !e) return 0;
  return Math.max(1, Math.round((e - s) / 86400000) + 1);
};

// ISO 8601 duration "PT2H30M" / "PT45M" / "PT3H" -> "2h 30m" / "45m" / "3h"
export const durationToHours = (duration) => {
  if (!duration) return "";
  const m = /^PT(?:(\d+)H)?(?:(\d+)M)?$/.exec(duration);
  if (!m) return duration;
  const parts = [];
  if (m[1] && +m[1] > 0) parts.push(`${+m[1]}h`);
  if (m[2] && +m[2] > 0) parts.push(`${+m[2]}m`);
  return parts.join(" ") || "0m";
};

const pad = (n) => String(n).padStart(2, "0");
export const toISODate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
export const todayISO = () => toISODate(new Date());
export const addDaysISO = (iso, days) => {
  const d = parseLocalDate(iso) || new Date();
  d.setDate(d.getDate() + days);
  return toISODate(d);
};
