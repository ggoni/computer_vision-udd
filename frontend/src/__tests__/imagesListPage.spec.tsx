import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImagesListPage from '../pages/ImagesListPage';
import * as client from '../api/client';
import { renderWithProviders } from '../test-utils';
import type { ImageResponse, PaginatedResponse } from '../api/types';

const makePage = (page: number): PaginatedResponse<ImageResponse> => ({
  items: [
    {
      id: `img-${page}-1`,
      filename: `file-${page}-1.png`,
      original_url: null,
      storage_path: `2025/11/12/file-${page}-1.png`,
      file_size: 2048,
      status: 'uploaded',
      upload_timestamp: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  total: 2,
  page,
  page_size: 10,
  pages: 2,
  has_next: page < 2,
  has_previous: page > 1,
});

vi.spyOn(client, 'listImages').mockImplementation(async (params: any) => makePage(params.page || 1));

describe('ImagesListPage', () => {
  it('renders first page and paginates to next', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ImagesListPage />);
    // Wait for first image row
    await screen.findByText(/file-1-1.png/);
    expect(screen.getByText(/Página 1 \/ 2/)).toBeInTheDocument();
    const nextBtn = screen.getByRole('button', { name: /siguiente/i });
    await user.click(nextBtn);
    await waitFor(() => expect(screen.getByText(/Página 2 \/ 2/)).toBeInTheDocument());
    expect(client.listImages).toHaveBeenCalledWith({ page: 2, page_size: 10, status: undefined, filename_substr: undefined });
  });
});
