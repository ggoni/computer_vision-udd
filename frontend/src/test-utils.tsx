import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './auth/AuthContext';
import { ToastProvider } from './components/Toast';
import { BrowserRouter } from 'react-router-dom';
import { render } from '@testing-library/react';

export function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  return render(
    <AuthProvider>
      <ToastProvider>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>{ui}</BrowserRouter>
        </QueryClientProvider>
      </ToastProvider>
    </AuthProvider>
  );
}
