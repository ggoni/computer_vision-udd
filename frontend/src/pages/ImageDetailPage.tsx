import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getImage, analyzeImage, listImageDetections } from '../api/client';
import type { ImageResponse, DetectionResponse } from '../api/types';
import DetectionsOverlay from '../components/DetectionsOverlay';

const ImageDetailPage: React.FC = () => {
  const { id } = useParams();
  const [showDetections, setShowDetections] = useState(false);

  const queryClient = useQueryClient();
  const imgQuery = useQuery<ImageResponse>({
    queryKey: ['image', id],
    queryFn: () => getImage(id!),
    // Hydrate from any cached images list pages to avoid loading flicker
    initialData: () => {
      const candidates = queryClient.getQueriesData<{ items: ImageResponse[] }>( { queryKey: ['images'] } );
      for (const [, data] of candidates) {
        if (data?.items) {
          const found = data.items.find((i) => i.id === id);
          if (found) return found;
        }
      }
      return undefined;
    },
    // Assume hydrated data was updated very recently; conservative timestamp
    initialDataUpdatedAt: Date.now() - 10_000,
  });
  const detQuery = useQuery<DetectionResponse[]>({
    queryKey: ['image-dets', id, showDetections],
    queryFn: () => listImageDetections(id!),
    enabled: !!id && showDetections,
  });

  const analyze = useMutation({
    mutationFn: async () => analyzeImage(id!),
    onSuccess: () => setShowDetections(true),
  });

  if (imgQuery.isLoading) return <p>Cargando...</p>;
  if (imgQuery.isError) return <p>Error cargando imagen</p>;

  const img = imgQuery.data!;
  const fileUrl = `/api/v1/images/${img.id}/file`;

  return (
    <div>
      <h2>{img.filename}</h2>
      <p>Estado: {img.status}</p>
      <button onClick={() => analyze.mutate()} disabled={analyze.isPending}>Analizar</button>{' '}
      <button onClick={() => setShowDetections((s) => !s)} disabled={detQuery.isLoading}>
        {showDetections ? 'Ocultar Detecciones' : 'Mostrar Detecciones'}
      </button>
      <div style={{ marginTop: '1rem' }}>
        {showDetections && detQuery.data && detQuery.data.length > 0 ? (
          <DetectionsOverlay imageUrl={fileUrl} detections={detQuery.data} />
        ) : (
          <img src={fileUrl} style={{ maxWidth: 640, width: '100%' }} />
        )}
      </div>
    </div>
  );
};

export default ImageDetailPage;
