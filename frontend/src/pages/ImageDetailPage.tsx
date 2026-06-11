import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getImage, analyzeImage, listImageDetections } from '../api/client';
import type { ImageResponse, DetectionResponse, AnalysisResult, ImageClassification } from '../api/types';
import DetectionsOverlay from '../components/DetectionsOverlay';

const ImageDetailPage: React.FC = () => {
  const { id } = useParams();
  const [showDetections, setShowDetections] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const queryClient = useQueryClient();
  const imgQuery = useQuery<ImageResponse>({
    queryKey: ['image', id],
    queryFn: () => getImage(id!),
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
    initialDataUpdatedAt: Date.now() - 10_000,
  });
  const detQuery = useQuery<DetectionResponse[]>({
    queryKey: ['image-dets', id, showDetections],
    queryFn: () => listImageDetections(id!),
    enabled: !!id && showDetections,
  });

  const analyze = useMutation({
    mutationFn: async () => analyzeImage(id!),
    onSuccess: (result) => {
      setAnalysisResult(result);
      setShowDetections(true);
      queryClient.invalidateQueries({ queryKey: ['image', id] });
      queryClient.invalidateQueries({ queryKey: ['image-dets', id] });
    },
  });

  if (imgQuery.isLoading) return <p>Cargando...</p>;
  if (imgQuery.isError) return <p>Error cargando imagen</p>;

  const img = imgQuery.data!;
  const fileUrl = `/api/v1/images/${img.id}/file`;
  const ocr = analysisResult?.text_extraction;
  const cls: ImageClassification | null | undefined = analysisResult?.classification;

  return (
    <div>
      <h2>{img.filename}</h2>
      <p>Estado: {img.status}</p>
      <button onClick={() => analyze.mutate()} disabled={analyze.isPending}>
        {analyze.isPending ? 'Analizando...' : 'Analizar'}
      </button>{' '}
      <button onClick={() => setShowDetections((s) => !s)} disabled={detQuery.isLoading}>
        {showDetections ? 'Ocultar Detecciones' : 'Mostrar Detecciones'}
      </button>
      {cls && (
        <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#ffffff', borderRadius: 6, border: '1px solid #ddd' }}>
          <strong style={{ color: '#000000' }}>Clasificacion (Gemini):</strong>{' '}
          {cls.error ? (
            <span style={{ color: 'red' }}>Error: {cls.error}</span>
          ) : cls.objects.length === 0 ? (
            <span style={{ color: '#888' }}>Sin resultados</span>
          ) : (
            <span style={{ color: '#000000' }}>
              {cls.objects.map((o) => `${o.label} (${(o.confidence * 100).toFixed(0)}%)`).join(', ')}
            </span>
          )}
        </div>
      )}
      {ocr && (
        <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#ffffff', borderRadius: 6, border: '1px solid #ddd' }}>
          <strong style={{ color: '#000000' }}>Texto extraido:</strong>{' '}
          {ocr.error ? (
            <span style={{ color: 'red' }}>Error OCR: {ocr.error}</span>
          ) : ocr.text ? (
            <span style={{ color: '#000000' }}>{ocr.text}</span>
          ) : (
            <span style={{ color: '#888' }}>No se encontro texto manuscrito</span>
          )}
        </div>
      )}
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
