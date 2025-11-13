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
  const { data, isLoading, error } = useQuery<
    PaginatedResponse<ImageResponse>,
    Error,
    PaginatedResponse<AugImage>
  >({
    queryKey: ['images', page, status, filenameFilter],
    queryFn: () => listImages({ page, page_size: pageSize, status: status || undefined, filename_substr: filenameFilter || undefined }),
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
        <input placeholder="Nombre contiene" value={filenameFilter} onChange={(e) => setFilenameFilter(e.target.value)} />
        <button onClick={() => setPage(1)}>Aplicar Filtros</button>
      </div>
      {isLoading && <p>Cargando...</p>}
      {error && <p style={{ color: '#ef4444' }}>{(error as any).message}</p>}
      {data && (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Estado</th>
                <th>Tamaño (KB)</th>
                <th>Subida</th>
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
