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
              <h1>CV Dashboard</h1>
              <nav>
                <Link to="/upload">Upload</Link>{' | '}
                <Link to="/images">Images</Link>{' | '}
                <Link to="/detections">Detections</Link>
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
