import { ImageResponse, DetectionResponse, PaginatedResponse } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Global token reference for API client
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  // When body is FormData, don't create Headers object
  // Browser must set Content-Type with boundary automatically
  const isFormData = init?.body instanceof FormData;

  let headers: HeadersInit | undefined;
  if (isFormData) {
    // For FormData, only add auth header if needed, don't use Headers object
    headers = authToken ? { 'Authorization': `Bearer ${authToken}` } : undefined;
  } else {
    // For non-FormData, use Headers object as before
    headers = new Headers(init?.headers);
    if (authToken) {
      (headers as Headers).set('Authorization', `Bearer ${authToken}`);
    }
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

export async function uploadImage(file: File): Promise<ImageResponse> {
  const form = new FormData();
  form.append('file', file);
  return request<ImageResponse>('/api/v1/images/upload', {
    method: 'POST',
    body: form,
  });
}

export async function getImage(id: string): Promise<ImageResponse> {
  return request<ImageResponse>(`/api/v1/images/${id}`);
}

export async function listImages(params: { page?: number; page_size?: number; status?: string; filename_substr?: string } = {}): Promise<PaginatedResponse<ImageResponse>> {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') q.append(k, String(v));
  });
  return request<PaginatedResponse<ImageResponse>>(`/api/v1/images?${q.toString()}`);
}

export async function analyzeImage(id: string): Promise<DetectionResponse[]> {
  return request<DetectionResponse[]>(`/api/v1/images/${id}/analyze`, { method: 'POST' });
}

export async function listImageDetections(id: string): Promise<DetectionResponse[]> {
  return request<DetectionResponse[]>(`/api/v1/images/${id}/detections`);
}

export async function listDetections(params: { page?: number; page_size?: number; label?: string; min_confidence?: number } = {}): Promise<PaginatedResponse<DetectionResponse>> {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') q.append(k, String(v));
  });
  return request<PaginatedResponse<DetectionResponse>>(`/api/v1/detections?${q.toString()}`);
}
