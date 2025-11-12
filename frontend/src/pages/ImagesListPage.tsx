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

  const { data, isLoading, error } = useQuery<PaginatedResponse<ImageResponse>>({
    queryKey: ['images', page, status, filenameFilter],
    queryFn: () => listImages({ page, page_size: pageSize, status: status || undefined, filename_substr: filenameFilter || undefined }),
    keepPreviousData: true,
  });

  return (
    <div>
      <h2>Images</h2>
      <div className="input-row">
        <input placeholder="Status" value={status} onChange={(e) => setStatus(e.target.value)} />
        <input placeholder="Filename contains" value={filenameFilter} onChange={(e) => setFilenameFilter(e.target.value)} />
        <button onClick={() => setPage(1)}>Apply Filters</button>
      </div>
      {isLoading && <p>Loading...</p>}
      {error && <p style={{ color: '#ef4444' }}>{(error as any).message}</p>}
      {data && (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Status</th>
                <th>Size (KB)</th>
                <th>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((img) => (
                <tr key={img.id}>
                  <td><Link to={`/images/${img.id}`}>{img.filename}</Link></td>
                  <td>{img.status}</td>
                  <td>{(img.file_size / 1024).toFixed(1)}</td>
                  <td>{new Date(img.upload_timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: '.75rem', display: 'flex', gap: '.5rem' }}>
            <button disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Prev</button>
            <span>Page {page} / {data.pages}</span>
            <button disabled={!data.has_next} onClick={() => setPage((p) => p + 1)}>Next</button>
          </div>
        </>
      )}
    </div>
  );
};

export default ImagesListPage;
