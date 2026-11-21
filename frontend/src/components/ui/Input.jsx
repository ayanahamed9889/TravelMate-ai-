import { useId } from 'react';

export default function Input({ label, error, className = '', id, ...props }) {
  const auto = useId();
  const inputId = id || auto;
  return (
    <div className="w-full">
      {label && <label htmlFor={inputId} className="label">{label}</label>}
      <input
        id={inputId}
        aria-invalid={!!error}
        {...props}
        className={`field ${error ? 'border-red-400' : ''} ${className}`}
      />
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  );
}
