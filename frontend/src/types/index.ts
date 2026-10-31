export interface User {
  id: number;
  email: string;
  username: string;
  role: 'customer' | 'merchant' | 'admin';
  avatar_url?: string;
  merchant_id?: number;
}

export interface Merchant {
  id: number;
  business_name: string;
  description: string;
  category: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  phone: string;
  is_verified: boolean;
  trust_score: number;
  distance_km?: number;
  distance_miles?: number;
  products_count?: number;
  product_count?: number;
}

export interface Product {
  id: number;
  merchant_id: number;
  merchant_name?: string;
  merchant_city?: string;
  merchant_verified?: boolean;
  merchant_trust_score?: number;
  title: string;
  description: string;
  category: string;
  price: number;
  inventory: number;
  image_url: string;
  tags: string[];
  distance_km?: number;
  recommendation_score?: number;
  similarity_score?: number;
  explanation?: string;
}

export interface Detection {
  timestamp: number;
  box: [number, number, number, number];
  label: string;
  confidence: number;
  product_id?: number;
  crop_path?: string;
  product_info?: {
    id: number;
    title: string;
    price: number;
    image_url: string;
    merchant: string;
  };
}

export interface VideoItem {
  id: number;
  title: string;
  description: string;
  video_url: string;
  thumbnail_url: string;
  duration: number;
  detections: Detection[];
  featured_products?: any[];
}

export interface ReviewItem {
  id: number;
  username: string;
  rating: number;
  comment: string;
  sentiment_score: number;
  sentiment_label: string;
  created_at: string;
}

export interface FraudFlagItem {
  id: number;
  target_type: string;
  target_id: number;
  target_name: string;
  risk_score: number;
  reasons: string[];
  status: 'pending' | 'approved' | 'dismissed';
  flagged_at: string;
}

export interface SystemHealth {
  status: string;
  database: {
    status: string;
    type?: string;
    users_count: number;
    merchants_count: number;
    products_count: number;
    videos_count: number;
  };
  computer_vision: {
    model: string;
    status: string;
    weights_path: string;
  };
  vector_search: {
    engine: string;
    status: string;
    indexed_items_count: number;
    vector_dimension: number;
  };
  ai_chatbot: {
    gemini_api_configured: boolean;
    fallback_mode: string;
  };
  storage: {
    free_space_gb: number;
  };
}
