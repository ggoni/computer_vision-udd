import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { uploadImage } from '../api/client';
import type { ImageResponse } from '../api/types';
import { useToasts } from './Toast';

interface Props {
  onUploaded: (img: ImageResponse) => void;
}

const ImageUploadForm: React.FC<Props> = ({ onUploaded }) => {
  const [file, setFile] = useState<File | null>(null);
  const { pushToast } = useToasts();

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected');
      return uploadImage(file);
    },
    onSuccess: (data) => {
      pushToast(`Subido: ${data.filename}`);
      onUploaded(data);
      setFile(null);
    },
    onError: (err: any) => pushToast(err.message, 'error'),
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        mutation.mutate();
      }}
    >
      <div className="input-row">
        <input
          type="file"
          accept="image/*"
          data-testid="file-input"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button type="submit" disabled={!file || mutation.isPending}>
          {mutation.isPending ? 'Subiendo...' : 'Subir'}
        </button>
      </div>
      {mutation.isError && <p style={{ color: '#ef4444' }}>{(mutation.error as any)?.message}</p>}
    </form>
  );
};

export default ImageUploadForm;
