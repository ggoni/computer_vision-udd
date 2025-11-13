import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ToastProvider } from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';
import UploadPage from './pages/UploadPage';
import ImagesListPage from './pages/ImagesListPage';
import ImageDetailPage from './pages/ImageDetailPage';
import DetectionsPage from './pages/DetectionsPage';
import { ToastViewport } from './components/Toast';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <header>
              <h1>Panel de Visión Computacional</h1>
              <nav>
                <Link to="/upload">Subir</Link>{' | '}
                <Link to="/images">Imágenes</Link>{' | '}
                <Link to="/detections">Detecciones</Link>
              </nav>
            </header>
            <main>
              <ErrorBoundary>
                <Routes>
                  <Route path="/" element={<UploadPage />} />
                  <Route path="/upload" element={<UploadPage />} />
                  <Route path="/images" element={<ImagesListPage />} />
                  <Route path="/images/:id" element={<ImageDetailPage />} />
                  <Route path="/detections" element={<DetectionsPage />} />
                </Routes>
              </ErrorBoundary>
            </main>
            <ToastViewport />
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
