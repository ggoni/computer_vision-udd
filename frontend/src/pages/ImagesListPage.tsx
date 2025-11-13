import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listImages } from '../api/client';
import type { ImageResponse, PaginatedResponse } from '../api/types';
import { Link } from 'react-router-dom';

const ImagesListPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [status, setStatus] = useState('');
  const [filenameFilter, setFilenameFilter] = useState('');

  type AugImage = ImageResponse & { file_size_kb: number; upload_local: string };
  const { data, isLoading, error, refetch } = useQuery<
    PaginatedResponse<ImageResponse>,
    Error,
    PaginatedResponse<AugImage>
  >({
    queryKey: ['images', page, status, filenameFilter],
    queryFn: () => listImages({ page, page_size: pageSize, status: status || undefined, filename_substr: filenameFilter || undefined }),
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    select: (resp) => ({
      ...resp,
      items: resp.items.map((img) => ({
        ...img,
        file_size_kb: img.file_size / 1024,
        upload_local: new Date(img.upload_timestamp).toLocaleString(),
      })),
    }) as PaginatedResponse<AugImage>,
  });

  return (
    <div>
      <h2>Imágenes</h2>
      <div className="input-row">
        <input placeholder="Estado" value={status} onChange={(e) => setStatus(e.target.value)} />
        <input placeholder="El nombre contiene" value={filenameFilter} onChange={(e) => setFilenameFilter(e.target.value)} />
        <button onClick={() => setPage(1)} disabled={isLoading}>
          {isLoading ? 'Cargando...' : 'Aplicar Filtros'}
        </button>
      </div>
      {isLoading && <p>Cargando...</p>}
      {error && (
        <div style={{ color: '#ef4444', padding: '1rem', border: '1px solid #ef4444', borderRadius: '4px', margin: '1rem 0' }}>
          <p><strong>Error al cargar imágenes:</strong> {(error as any).message}</p>
          <button 
            onClick={() => refetch()} 
            style={{ marginTop: '0.5rem', padding: '0.5rem 1rem', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Reintentar
          </button>
        </div>
      )}
      {data && (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Nombre de archivo</th>
                <th>Estado</th>
                <th>Tamaño (KB)</th>
                <th>Subido</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((img: AugImage) => (
                <tr key={img.id}>
                  <td><Link to={`/images/${img.id}`}>{img.filename}</Link></td>
                  <td>{img.status}</td>
                  <td>{img.file_size_kb.toFixed(1)}</td>
                  <td>{img.upload_local}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: '.75rem', display: 'flex', gap: '.5rem' }}>
            <button disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Anterior</button>
            <span>Página {page} / {data.pages}</span>
            <button disabled={!data.has_next} onClick={() => setPage((p) => p + 1)}>Siguiente</button>
          </div>
        </>
      )}
    </div>
  );
};

export default ImagesListPage;
