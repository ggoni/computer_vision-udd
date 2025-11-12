import React, { useRef, useEffect, useState } from 'react';
import type { DetectionResponse } from '../api/types';

interface Props {
  imageUrl: string;
  detections: DetectionResponse[];
  maxWidth?: number;
}

const DetectionsOverlay: React.FC<Props> = ({ imageUrl, detections, maxWidth = 640 }) => {
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [dims, setDims] = useState<{ w: number; h: number }>({ w: 0, h: 0 });

  useEffect(() => {
    if (imgRef.current && imgRef.current.complete) {
      setDims({ w: imgRef.current.naturalWidth, h: imgRef.current.naturalHeight });
    }
  }, [imageUrl]);

  const handleLoad = () => {
    if (imgRef.current) {
      setDims({ w: imgRef.current.naturalWidth, h: imgRef.current.naturalHeight });
    }
  };

  return (
    <div className="overlay-wrapper" style={{ maxWidth }}>
      <img ref={imgRef} src={imageUrl} onLoad={handleLoad} style={{ width: '100%', display: 'block' }} />
      {dims.w > 0 && (
        <div>
          {detections.map((d) => {
            const style: React.CSSProperties = {
              left: `${(d.bbox_xmin / dims.w) * 100}%`,
              top: `${(d.bbox_ymin / dims.h) * 100}%`,
              width: `${((d.bbox_xmax - d.bbox_xmin) / dims.w) * 100}%`,
              height: `${((d.bbox_ymax - d.bbox_ymin) / dims.h) * 100}%`,
            };
            return (
              <div key={d.id} className="bbox" style={style}>
                {d.label} {(d.confidence_score * 100).toFixed(1)}%
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DetectionsOverlay;
