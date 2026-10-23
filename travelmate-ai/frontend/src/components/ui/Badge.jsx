export default function Badge({ children, variant = "default", className = "" }) {
  const variants = {
    default: "bg-slate-100 text-slate-700",
    primary: "bg-indigo-50 text-primary",
    success: "bg-emerald-50 text-emerald-700",
    warning: "bg-amber-50 text-amber-700",
    danger: "bg-red-50 text-red-700",
    accent: "bg-orange-50 text-secondary",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold ${variants[variant] || variants.default} ${className}`}>
      {children}
    </span>
  );

}
