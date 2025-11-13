import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DetectionsPage from '../pages/DetectionsPage';
import * as client from '../api/client';
// rely on setupTests for matcher extension

import { renderWithProviders } from '../test-utils';
import type { DetectionResponse, PaginatedResponse } from '../api/types';

const now = new Date().toISOString();
const makeDet = (id: string, label: string, conf: number): DetectionResponse => ({
  id, image_id: 'img-1', label, confidence_score: conf, bbox_xmin: 0, bbox_ymin: 0, bbox_xmax: 1, bbox_ymax: 1, created_at: now, updated_at: now
});

const pageData = (labelFilter?: string, min?: number): PaginatedResponse<DetectionResponse> => {
  const base = [
    makeDet('d1', 'cat', 0.95),
    makeDet('d2', 'dog', 0.60),
    makeDet('d3', 'cat', 0.90),
  ];
  let items = base;
  if (labelFilter) items = items.filter(i => i.label === labelFilter);
  if (min !== undefined) items = items.filter(i => i.confidence_score >= min);
  return { items, total: items.length, page: 1, page_size: 20, pages: 1, has_next: false, has_previous: false };
};

describe('DetectionsPage', () => {
  it('filters by label and min confidence', async () => {
    const listDetectionsMock = vi.spyOn(client, 'listDetections').mockImplementation(async (params: any) => 
      pageData(params.label, params.min_confidence)
    );
    
    const user = userEvent.setup();
    renderWithProviders(<DetectionsPage />);
    // initial load - wait for table to appear
    await screen.findByRole('table');
    expect(screen.getAllByText(/cat/).length).toBeGreaterThan(0);
    expect(screen.getByText(/dog/)).toBeTruthy();
    
    // apply label filter
    await user.type(screen.getByPlaceholderText(/Etiqueta/), 'cat');
    await user.click(screen.getByRole('button', { name: /Aplicar/i }));
    await waitFor(() => expect(screen.queryByText(/dog/)).toBeNull());
    
    // apply min confidence
    await user.clear(screen.getByPlaceholderText(/Conf mínima/));
    await user.type(screen.getByPlaceholderText(/Conf mínima/), '0.93');
    await user.click(screen.getByRole('button', { name: /Aplicar/i }));
    await waitFor(() => {
      expect(screen.getAllByText(/cat/).length).toBe(1); // only high confidence cat remains
      expect(screen.queryByText(/dog/)).toBeNull();
    });
    
    // Verify API was called and functional behavior is correct
    expect(listDetectionsMock.mock.calls.length).toBeGreaterThanOrEqual(3);
    
    listDetectionsMock.mockRestore();
  });
});
