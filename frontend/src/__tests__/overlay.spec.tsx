import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DetectionsOverlay from '../components/DetectionsOverlay';
import type { DetectionResponse } from '../api/types';

const now = new Date().toISOString();
const mockDetections: DetectionResponse[] = [
  {
    id: '1',
    image_id: '1',
    label: 'object',
    confidence_score: 0.9,
    bbox_xmin: 0,
    bbox_ymin: 0,
    bbox_xmax: 100,
    bbox_ymax: 50,
    created_at: now,
    updated_at: now
  }
];

describe('DetectionsOverlay', () => {
  it('positions and sizes bounding boxes proportionally', () => {
    render(<DetectionsOverlay imageUrl="/fake.png" detections={mockDetections} />);
    const img = screen.getByRole('img');
    // Mock natural dimensions
    Object.defineProperty(img, 'naturalWidth', { value: 200, configurable: true });
    Object.defineProperty(img, 'naturalHeight', { value: 100, configurable: true });
    fireEvent.load(img);
    const box = screen.getByText(/object/);
    // Width should be (100/200)*100 = 50% and height (50/100)*100 = 50%
    expect(box).toHaveStyle({ width: '50%', height: '50%', left: '0%', top: '0%' });
  });
});
