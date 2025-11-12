export interface ImageResponse {
  id: string;
  filename: string;
  original_url?: string | null;
  storage_path: string;
  file_size: number;
  status: string;
  upload_timestamp: string;
  created_at: string;
  updated_at: string;
}

export interface DetectionResponse {
  id: string;
  image_id: string;
  label: string;
  confidence_score: number;
  bbox_xmin: number;
  bbox_ymin: number;
  bbox_xmax: number;
  bbox_ymax: number;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
  has_next: boolean;
  has_previous: boolean;
}
