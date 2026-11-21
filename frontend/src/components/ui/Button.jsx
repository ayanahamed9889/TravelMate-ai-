export default function Button({ children, variant = 'primary', className = '', type = 'button', ...props }) {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    dark: 'btn-dark',
    ghost: 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors disabled:opacity-50',
  };
  return (
    <button type={type} className={`${variants[variant] || variants.primary} ${className}`} {...props}>
      {children}
    </button>
  );
}
