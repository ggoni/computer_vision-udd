import React, { useState } from 'react';
import ImageUploadForm from '../components/ImageUploadForm';
import type { ImageResponse } from '../api/types';

const UploadPage: React.FC = () => {
  const [lastImage, setLastImage] = useState<ImageResponse | null>(null);
  return (
    <div>
      <h2>Upload Image</h2>
      <ImageUploadForm onUploaded={setLastImage} />
      {lastImage && (
        <div style={{ marginTop: '1rem' }} className="card">
          <h3>{lastImage.filename}</h3>
          <p>Size: {(lastImage.file_size / 1024).toFixed(2)} KB</p>
          <p>Status: {lastImage.status}</p>
          <a href={`/api/v1/images/${lastImage.id}/file`} target="_blank" rel="noreferrer">Download</a>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
