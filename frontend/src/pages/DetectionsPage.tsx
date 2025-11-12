import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listDetections } from '../api/client';
import type { DetectionResponse, PaginatedResponse } from '../api/types';

const DetectionsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [label, setLabel] = useState('');
  const [minConf, setMinConf] = useState<number | ''>('');

  const { data, isLoading, error } = useQuery<PaginatedResponse<DetectionResponse>>({
    queryKey: ['dets', page, label, minConf],
    queryFn: () => listDetections({ page, page_size: 20, label: label || undefined, min_confidence: minConf === '' ? undefined : Number(minConf) }),
    keepPreviousData: true,
  });

  return (
    <div>
      <h2>Detections</h2>
      <div className="input-row">
        <input placeholder="Label" value={label} onChange={(e) => setLabel(e.target.value)} />
        <input
          type="number"
            placeholder="Min conf"
            value={minConf}
            onChange={(e) => setMinConf(e.target.value === '' ? '' : Number(e.target.value))}
        />
        <button onClick={() => setPage(1)}>Apply</button>
      </div>
      {isLoading && <p>Loading...</p>}
      {error && <p style={{ color: '#ef4444' }}>{(error as any).message}</p>}
      {data && (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Label</th>
                <th>Confidence</th>
                <th>Image</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((d) => (
                <tr key={d.id}>
                  <td>{d.label}</td>
                  <td>{(d.confidence_score * 100).toFixed(1)}%</td>
                  <td>{d.image_id.slice(0, 8)}…</td>
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

export default DetectionsPage;
