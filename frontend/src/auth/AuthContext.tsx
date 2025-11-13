import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { setAuthToken } from '../api/client';

interface AuthState {
  token: string | null;
  setToken: (t: string | null) => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  
  // Sync token with API client whenever it changes
  useEffect(() => {
    setAuthToken(token);
  }, [token]);
  
  return <AuthContext.Provider value={{ token, setToken }}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthState => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
