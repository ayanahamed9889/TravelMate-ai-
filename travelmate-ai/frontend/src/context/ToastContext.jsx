import { createContext, useState, useCallback, useContext, useMemo, useRef } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

const ToastContext = createContext(null);

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within a ToastProvider');
  return ctx;
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const nextId = useRef(1);

  const remove = useCallback((id) => setToasts((prev) => prev.filter((t) => t.id !== id)), []);

  const addToast = useCallback((message, type = 'success') => {
    const id = nextId.current++;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => remove(id), 4500);
  }, [remove]);

  const value = useMemo(() => ({ addToast }), [addToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-4 right-4 left-4 sm:left-auto sm:bottom-6 sm:right-6 z-[9999] space-y-2" aria-live="polite">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border bg-white sm:min-w-[280px] sm:max-w-sm ml-auto ${t.type === 'success' ? 'border-emerald-200' : 'border-red-200'}`}
          >
            {t.type === 'success'
              ? <CheckCircle size={18} className="text-emerald-500 shrink-0" />
              : <XCircle size={18} className="text-red-500 shrink-0" />}
            <p className="text-sm font-medium text-slate-700 flex-1">{t.message}</p>
            <button onClick={() => remove(t.id)} aria-label="Dismiss"><X size={14} className="text-slate-400" /></button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
