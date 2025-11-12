import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getImage, analyzeImage, listImageDetections } from '../api/client';
import type { ImageResponse, DetectionResponse } from '../api/types';
import DetectionsOverlay from '../components/DetectionsOverlay';

const ImageDetailPage: React.FC = () => {
  const { id } = useParams();
  const [showDetections, setShowDetections] = useState(false);

  const imgQuery = useQuery<ImageResponse>({ queryKey: ['image', id], queryFn: () => getImage(id!) });
  const detQuery = useQuery<DetectionResponse[]>({
    queryKey: ['image-dets', id, showDetections],
    queryFn: () => listImageDetections(id!),
    enabled: !!id && showDetections,
  });

  const analyze = useMutation({
    mutationFn: async () => analyzeImage(id!),
    onSuccess: () => setShowDetections(true),
  });

  if (imgQuery.isLoading) return <p>Loading...</p>;
  if (imgQuery.isError) return <p>Error loading image</p>;

  const img = imgQuery.data!;
  const fileUrl = `/api/v1/images/${img.id}/file`;

  return (
    <div>
      <h2>{img.filename}</h2>
      <p>Status: {img.status}</p>
      <button onClick={() => analyze.mutate()} disabled={analyze.isPending}>Analyze</button>{' '}
      <button onClick={() => setShowDetections((s) => !s)} disabled={detQuery.isLoading}>
        {showDetections ? 'Hide Detections' : 'Show Detections'}
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
