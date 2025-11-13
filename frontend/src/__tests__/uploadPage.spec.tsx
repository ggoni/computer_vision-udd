import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadPage from '../pages/UploadPage';
import * as client from '../api/client';
import { renderWithProviders } from '../test-utils';

// Mock uploadImage
vi.spyOn(client, 'uploadImage').mockImplementation(async (file: File) => {
  return {
    id: 'img-1',
    filename: file.name,
    original_url: null,
    storage_path: `2025/11/12/${file.name}`,
    file_size: file.size,
    status: 'uploaded',
    upload_timestamp: new Date().toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
});

describe('UploadPage', () => {
  it('uploads and displays last image card + toast', async () => {
    const user = userEvent.setup();
    renderWithProviders(<UploadPage />);
  const input = screen.getByTestId('file-input') as HTMLInputElement;
    const file = new File(['dummy'], 'test.png', { type: 'image/png' });
    await user.upload(input, file);
    await user.click(screen.getByRole('button', { name: /subir/i }));
    // Wait for toast and card
  const card = await screen.findByText('test.png');
    expect(card).toBeInTheDocument();
    // Toast container should contain Uploaded message
    const toast = await screen.findByText(/Subido: test.png/);
    expect(toast).toBeInTheDocument();
    expect(client.uploadImage).toHaveBeenCalled();
  });
});
