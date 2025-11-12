import React, { createContext, useContext, useState } from 'react';

interface Toast { id: string; message: string; variant?: 'info' | 'error'; }
interface ToastCtx { pushToast: (msg: string, variant?: 'info' | 'error') => void; }

const ToastContext = createContext<ToastCtx | null>(null);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const pushToast = (message: string, variant: 'info' | 'error' = 'info') => {
    const id = crypto.randomUUID();
    setToasts((t) => [...t, { id, message, variant }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4000);
  };

  return (
    <ToastContext.Provider value={{ pushToast }}>
      {children}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className="toast" style={{ borderLeftColor: t.variant === 'error' ? '#dc2626' : '#2563eb' }}>
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export function useToasts() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToasts must be used within ToastProvider');
  return ctx;
}

export const ToastViewport: React.FC = () => null;
