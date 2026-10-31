import { User, Merchant, Product, VideoItem, SystemHealth, FraudFlagItem } from '../types';

const isElectron = typeof window !== 'undefined' && (
  window.location.protocol === 'file:' ||
  window.location.protocol === 'app:' ||
  window.location.hostname === '' ||
  Boolean((window as any).electronAPI) ||
  Boolean((window as any).electron) ||
  (typeof navigator !== 'undefined' && navigator.userAgent.toLowerCase().includes('electron'))
);

export const BACKEND_HOST = (typeof window !== 'undefined' && (window as any).SCROLLIX_API_URL)
  ? (window as any).SCROLLIX_API_URL
  : (isElectron ? 'http://127.0.0.1:8000' : '');

export const API_BASE = `${BACKEND_HOST}/api`;

export function getMediaUrl(path?: string | null): string {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('data:')) {
    return path;
  }
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${BACKEND_HOST}${cleanPath}`;
}

export function formatPrice(amount?: number | null): string {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  return `₹${Math.round(amount).toLocaleString('en-IN')}`;
}

function getHeaders(isFormData: boolean = false): HeadersInit {
  const headers: Record<string, string> = {};
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  const token = localStorage.getItem('scrollix_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function fetchWithHandling(url: string, options: RequestInit = {}): Promise<Response> {
  try {
    return await fetch(url, options);
  } catch (err: any) {
    console.error(`[API Network Error] ${url}:`, err);
    throw new Error(`Connection error: Could not reach Scrollix AI backend at ${BACKEND_HOST || 'http://127.0.0.1:8000'}. Ensure the backend service is running.`);
  }
}

export const api = {
  // Auth
  async register(data: any) {
    const res = await fetchWithHandling(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Registration failed');
    return res.json();
  },

  async login(username_or_email: string, password: string) {
    const res = await fetchWithHandling(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ username_or_email, password })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Invalid login');
    return res.json();
  },

  async demoSwitchRole(role: string) {
    const res = await fetchWithHandling(`${API_BASE}/auth/demo-switch`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ role })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to switch demo role');
    return res.json();
  },

  async getMe() {
    const res = await fetchWithHandling(`${API_BASE}/auth/me`, {
      headers: getHeaders()
    });
    if (!res.ok) return null;
    return res.json();
  },

  // Feed & Recommendations
  async getFeed(lat?: number, lng?: number, limit = 15) {
    let url = `${API_BASE}/recommendations/feed?limit=${limit}`;
    if (lat !== undefined && lng !== undefined) {
      url += `&lat=${lat}&lng=${lng}`;
    }
    const res = await fetchWithHandling(url, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to load feed');
    return res.json() as Promise<Product[]>;
  },

  async getVideos(lat?: number, lng?: number) {
    let url = `${API_BASE}/recommendations/videos`;
    if (lat !== undefined && lng !== undefined) {
      url += `?lat=${lat}&lng=${lng}`;
    }
    const res = await fetchWithHandling(url, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to load videos');
    return res.json() as Promise<VideoItem[]>;
  },

  async recordInteraction(productId: number, interactionType: string, dwellTime = 0) {
    return fetchWithHandling(`${API_BASE}/products/${productId}/interact`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ interaction_type: interactionType, dwell_time: dwellTime })
    });
  },

  // Video Upload & CV
  async uploadVideo(file: File, title: string, description: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('description', description);

    const res = await fetchWithHandling(`${API_BASE}/videos/upload`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData
    });
    if (!res.ok) {
      let detail = 'Upload failed';
      try {
        const data = await res.json();
        detail = data.detail || detail;
      } catch {
        detail = `Server error HTTP ${res.status}`;
      }
      throw new Error(detail);
    }
    return res.json();
  },

  // Search
  async searchText(query: string, category?: string, minPrice?: number, maxPrice?: number) {
    const res = await fetchWithHandling(`${API_BASE}/search/text`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        query,
        category: category || null,
        min_price: minPrice || null,
        max_price: maxPrice || null,
        top_k: 12
      })
    });
    if (!res.ok) throw new Error('Search failed');
    return res.json() as Promise<Product[]>;
  },

  async searchVisual(file: File, category?: string, minPrice?: number, maxPrice?: number) {
    const formData = new FormData();
    formData.append('file', file);
    if (category) formData.append('category', category);
    if (minPrice) formData.append('min_price', minPrice.toString());
    if (maxPrice) formData.append('max_price', maxPrice.toString());

    const res = await fetchWithHandling(`${API_BASE}/search/visual`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData
    });
    if (!res.ok) {
      let detail = 'Visual search failed';
      try {
        const data = await res.json();
        detail = data.detail || detail;
      } catch {
        detail = `HTTP ${res.status}`;
      }
      throw new Error(detail);
    }
    return res.json() as Promise<Product[]>;
  },

  // Location & Maps
  async getPresetCities() {
    const res = await fetchWithHandling(`${API_BASE}/location/cities`);
    return res.json();
  },

  async reverseGeocode(lat: number, lng: number) {
    const res = await fetchWithHandling(`${API_BASE}/location/reverse-geocode?lat=${lat}&lng=${lng}`);
    if (!res.ok) throw new Error('Failed to reverse geocode coordinates');
    return res.json() as Promise<{
      city: string;
      display_name: string;
      latitude: number;
      longitude: number;
      match_type: string;
    }>;
  },

  async getDeviceLocation() {
    const res = await fetchWithHandling(`${API_BASE}/location/device-ip`);
    if (!res.ok) {
      let detail = 'Device location resolution failed';
      try {
        const data = await res.json();
        detail = data.detail || detail;
      } catch {
        detail = `HTTP ${res.status}`;
      }
      throw new Error(detail);
    }
    return res.json() as Promise<{
      latitude: number;
      longitude: number;
      city: string;
      source: string;
      provider?: string;
    }>;
  },

  async getNearbyMerchants(lat: number, lng: number, radiusKm = 25) {
    const res = await fetchWithHandling(`${API_BASE}/location/nearby-merchants?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`);
    if (!res.ok) throw new Error('Failed to load nearby merchants');
    return res.json();
  },

  async seedNearbyDemoMerchants(lat: number, lng: number, city?: string) {
    let url = `${API_BASE}/location/seed-nearby-demo?lat=${lat}&lng=${lng}`;
    if (city) url += `&city=${encodeURIComponent(city)}`;
    const res = await fetchWithHandling(url, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to seed nearby demo merchants');
    return res.json();
  },

  async getMerchants(city?: string, category?: string) {
    let url = `${API_BASE}/merchants`;
    const params = new URLSearchParams();
    if (city) params.append('city', city);
    if (category) params.append('category', category);
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetchWithHandling(url, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to load merchants');
    return res.json() as Promise<Merchant[]>;
  },

  async getMerchant(id: number) {
    const res = await fetchWithHandling(`${API_BASE}/merchants/${id}`);
    if (!res.ok) throw new Error('Merchant not found');
    return res.json();
  },

  // Products & Merchants
  async getProducts(params: Record<string, any> = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetchWithHandling(`${API_BASE}/products?${query}`);
    return res.json() as Promise<Product[]>;
  },

  async getProduct(id: number) {
    const res = await fetchWithHandling(`${API_BASE}/products/${id}`);
    if (!res.ok) throw new Error('Product not found');
    return res.json();
  },

  async createProduct(data: any) {
    const res = await fetchWithHandling(`${API_BASE}/products`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create product');
    return res.json();
  },

  async deleteProduct(id: number) {
    const res = await fetchWithHandling(`${API_BASE}/products/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to delete product');
    return res.json();
  },

  async addReview(productId: number, rating: number, comment: string) {
    const res = await fetchWithHandling(`${API_BASE}/products/${productId}/reviews`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ rating, comment })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to add review');
    return res.json();
  },

  async onboardMerchant(data: any) {
    const res = await fetchWithHandling(`${API_BASE}/merchants/onboard`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to onboard');
    return res.json();
  },

  // AI Shopping Assistant
  async chatAssistant(message: string, history: any[] = []) {
    const res = await fetchWithHandling(`${API_BASE}/assistant/chat`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ message, history })
    });
    if (!res.ok) throw new Error('Assistant query failed');
    return res.json();
  },

  async getAssistantConfig() {
    const res = await fetchWithHandling(`${API_BASE}/assistant/config`);
    return res.json();
  },

  async setAssistantKey(apiKey: string) {
    const res = await fetchWithHandling(`${API_BASE}/assistant/config`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ api_key: apiKey })
    });
    return res.json();
  },

  // Fraud & Moderation
  async getFraudFlags(status?: string) {
    const url = status ? `${API_BASE}/fraud/flags?status=${status}` : `${API_BASE}/fraud/flags`;
    const res = await fetchWithHandling(url, { headers: getHeaders() });
    return res.json() as Promise<FraudFlagItem[]>;
  },

  async runFraudScan() {
    const res = await fetchWithHandling(`${API_BASE}/fraud/scan`, {
      method: 'POST',
      headers: getHeaders()
    });
    return res.json();
  },

  async resolveFlag(flagId: number, action: 'approved' | 'dismissed', note = '') {
    const res = await fetchWithHandling(`${API_BASE}/fraud/flags/${flagId}/resolve`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ action, note })
    });
    return res.json();
  },

  // Analytics
  async getAnalytics(merchantId?: number) {
    const url = merchantId ? `${API_BASE}/analytics/dashboard?merchant_id=${merchantId}` : `${API_BASE}/analytics/dashboard`;
    const res = await fetchWithHandling(url, { headers: getHeaders() });
    return res.json();
  },

  // System Health
  async getHealth() {
    const res = await fetchWithHandling(`${API_BASE}/admin/health`);
    return res.json() as Promise<SystemHealth>;
  }
};
