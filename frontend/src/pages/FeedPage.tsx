import React, { useState, useEffect, useRef } from 'react';
import { 
  Heart, 
  Bookmark, 
  Share2, 
  ShoppingBag, 
  Eye, 
  Sparkles, 
  Volume2, 
  VolumeX, 
  Play, 
  Pause, 
  Layers,
  MapPin,
  ShieldCheck
} from 'lucide-react';
import { VideoItem, Product } from '../types';
import { api, getMediaUrl, formatPrice } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ProductModal } from '../components/ProductModal';

export const FeedPage: React.FC = () => {
  const { location } = useAuth();
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);
  const [muted, setMuted] = useState(true);
  const [likedVideoIds, setLikedVideoIds] = useState<Set<number>>(new Set());
  const [savedVideoIds, setSavedVideoIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadFeed();
  }, [location]);

  const loadFeed = async () => {
    setLoading(true);
    try {
      const [vData, pData] = await Promise.all([
        api.getVideos(location.lat ?? undefined, location.lng ?? undefined),
        api.getFeed(location.lat ?? undefined, location.lng ?? undefined, 10)
      ]);
      setVideos(vData);
      setProducts(pData);
    } catch (err) {
      console.error('Error loading feed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (video: VideoItem) => {
    const isLiked = likedVideoIds.has(video.id);
    const updated = new Set(likedVideoIds);
    if (isLiked) updated.delete(video.id);
    else updated.add(video.id);
    setLikedVideoIds(updated);

    // Record interaction on featured products
    if (video.featured_products && video.featured_products.length > 0) {
      const pId = video.featured_products[0].id;
      await api.recordInteraction(pId, isLiked ? 'unlike' : 'like');
    }
  };

  const handleSave = (video: VideoItem) => {
    const updated = new Set(savedVideoIds);
    if (updated.has(video.id)) updated.delete(video.id);
    else updated.add(video.id);
    setSavedVideoIds(updated);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px 40px' }}>
      {/* Feed Controls Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
            Smart <span className="text-gradient">Viral Video Feed</span>
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            AI-powered shop-ready video discovery with real-time YOLOv11 detections & location intelligence
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Toggle Bounding Boxes */}
          <button
            onClick={() => setShowBoundingBoxes(!showBoundingBoxes)}
            className="btn-secondary"
            style={{
              borderColor: showBoundingBoxes ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.1)',
              color: showBoundingBoxes ? '#38bdf8' : 'var(--text-muted)',
              fontSize: '12px',
              padding: '8px 14px'
            }}
          >
            <Layers size={15} />
            <span>YOLOv11 Bounding Boxes: {showBoundingBoxes ? 'ON' : 'OFF'}</span>
          </button>

          {/* Mute toggle */}
          <button
            onClick={() => setMuted(!muted)}
            className="btn-secondary"
            style={{ fontSize: '12px', padding: '8px 14px' }}
          >
            {muted ? <VolumeX size={15} /> : <Volume2 size={15} />}
            <span>{muted ? 'Muted' : 'Unmuted'}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-muted)' }}>
          Loading personalized recommendations & video AI streams...
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 520px) 1fr', gap: '32px' }}>
          {/* Left Column: Short-form Video Reels */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            {videos.map((video) => (
              <VideoCard
                key={video.id}
                video={video}
                showBoxes={showBoundingBoxes}
                isMuted={muted}
                isLiked={likedVideoIds.has(video.id)}
                isSaved={savedVideoIds.has(video.id)}
                onLike={() => handleLike(video)}
                onSave={() => handleSave(video)}
                onSelectProduct={(id) => setSelectedProductId(id)}
              />
            ))}
          </div>

          {/* Right Column: Personalized Hybrid Recommendations */}
          <div>
            <div className="glass-panel" style={{ padding: '24px', position: 'sticky', top: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <Sparkles size={18} color="var(--accent-cyan)" />
                <h3 style={{ fontSize: '18px', fontWeight: 700 }}>Personalized For You</h3>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '18px' }}>
                Ranked using hybrid content similarity, merchant proximity, and exploration decay.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {products.map((p) => (
                  <div
                    key={p.id}
                    className="glass-card"
                    onClick={() => setSelectedProductId(p.id)}
                    style={{
                      padding: '12px 14px',
                      display: 'flex',
                      gap: '14px',
                      cursor: 'pointer',
                      alignItems: 'center'
                    }}
                  >
                    <img
                      src={getMediaUrl(p.image_url)}
                      alt={p.title}
                      style={{ width: '64px', height: '64px', borderRadius: '10px', objectFit: 'cover' }}
                    />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                        <span style={{ fontSize: '13px', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {p.title}
                        </span>
                        <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                          {formatPrice(p.price)}
                        </span>
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '4px' }}>
                        {p.merchant_name} • {p.merchant_city}
                      </div>
                      {/* Explainability Pill */}
                      {p.explanation && (
                        <div style={{ fontSize: '10.5px', color: '#60a5fa', background: 'rgba(59,130,246,0.1)', padding: '2px 8px', borderRadius: '6px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          💡 {p.explanation}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Product Detail Modal */}
      <ProductModal
        productId={selectedProductId}
        onClose={() => setSelectedProductId(null)}
      />
    </div>
  );
};

// Video Card Subcomponent with Interactive Bounding Boxes
const VideoCard: React.FC<{
  video: VideoItem;
  showBoxes: boolean;
  isMuted: boolean;
  isLiked: boolean;
  isSaved: boolean;
  onLike: () => void;
  onSave: () => void;
  onSelectProduct: (id: number) => void;
}> = ({ video, showBoxes, isMuted, isLiked, isSaved, onLike, onSave, onSelectProduct }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(true);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  return (
    <div className="glass-panel" style={{ overflow: 'hidden', borderRadius: '18px', border: '1px solid rgba(255,255,255,0.1)' }}>
      {/* Video Container */}
      <div style={{ position: 'relative', width: '100%', height: '580px', backgroundColor: '#000' }}>
        <video
          ref={videoRef}
          src={getMediaUrl(video.video_url)}
          poster={getMediaUrl(video.thumbnail_url)}
          autoPlay
          loop
          muted={isMuted}
          playsInline
          onClick={togglePlay}
          style={{ width: '100%', height: '100%', objectFit: 'cover', cursor: 'pointer' }}
        />

        {/* Play/Pause Overlay Indicator on click */}
        <div
          onClick={togglePlay}
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: isPlaying ? 'transparent' : 'rgba(0,0,0,0.4)',
            cursor: 'pointer'
          }}
        >
          {!isPlaying && (
            <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Play size={30} color="white" />
            </div>
          )}
        </div>

        {/* YOLOv11 Bounding Box Overlay */}
        {showBoxes && video.detections && video.detections.length > 0 && (
          <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
            {video.detections.map((det, idx) => {
              // Normalize box coordinates assuming 640x640 base resolution
              const [x1, y1, x2, y2] = det.box;
              const leftPct = (x1 / 640) * 100;
              const topPct = (y1 / 640) * 100;
              const widthPct = ((x2 - x1) / 640) * 100;
              const heightPct = ((y2 - y1) / 640) * 100;

              return (
                <div
                  key={idx}
                  style={{
                    position: 'absolute',
                    left: `${Math.max(5, Math.min(85, leftPct))}%`,
                    top: `${Math.max(5, Math.min(80, topPct))}%`,
                    width: `${Math.max(20, Math.min(60, widthPct))}%`,
                    height: `${Math.max(20, Math.min(60, heightPct))}%`,
                    border: '2px solid #06b6d4',
                    borderRadius: '8px',
                    boxShadow: '0 0 14px rgba(6, 182, 212, 0.6)',
                    pointerEvents: 'auto',
                    cursor: det.product_id ? 'pointer' : 'default'
                  }}
                  onClick={() => det.product_id && onSelectProduct(det.product_id)}
                >
                  {/* Tag Pill */}
                  <div
                    style={{
                      position: 'absolute',
                      top: '-26px',
                      left: '0',
                      background: 'rgba(6, 182, 212, 0.9)',
                      color: '#000',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    <span>{det.label.toUpperCase()}</span>
                    <span>{Math.round(det.confidence * 100)}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Floating Right Actions */}
        <div style={{ position: 'absolute', right: '16px', bottom: '90px', display: 'flex', flexDirection: 'column', gap: '14px', zIndex: 20 }}>
          <button
            onClick={onLike}
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: isLiked ? 'rgba(244,63,94,0.3)' : 'rgba(0,0,0,0.6)',
              border: isLiked ? '1px solid #f43f5e' : '1px solid rgba(255,255,255,0.15)',
              color: isLiked ? '#f43f5e' : 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <Heart size={20} fill={isLiked ? '#f43f5e' : 'none'} />
          </button>

          <button
            onClick={onSave}
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: isSaved ? 'rgba(59,130,246,0.3)' : 'rgba(0,0,0,0.6)',
              border: isSaved ? '1px solid #3b82f6' : '1px solid rgba(255,255,255,0.15)',
              color: isSaved ? '#60a5fa' : 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer'
            }}
          >
            <Bookmark size={20} fill={isSaved ? '#60a5fa' : 'none'} />
          </button>

          <button
            onClick={() => {
              if (navigator.clipboard) navigator.clipboard.writeText(window.location.href);
              alert('Video link copied to clipboard!');
            }}
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: 'rgba(0,0,0,0.6)',
              border: '1px solid rgba(255,255,255,0.15)',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer'
            }}
          >
            <Share2 size={18} />
          </button>
        </div>

        {/* Bottom Video Metadata */}
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '20px', background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 100%)', zIndex: 10 }}>
          <h4 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '4px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>
            {video.title}
          </h4>
          <p style={{ fontSize: '12px', color: '#e5e7eb', marginBottom: '12px', lineHeight: 1.4, textShadow: '0 1px 2px rgba(0,0,0,0.8)' }}>
            {video.description}
          </p>

          {/* Featured Shop Drawer */}
          {video.featured_products && video.featured_products.length > 0 && (
            <div
              onClick={() => onSelectProduct(video.featured_products![0].id)}
              style={{
                background: 'rgba(0,0,0,0.8)',
                backdropFilter: 'blur(10px)',
                padding: '8px 12px',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                cursor: 'pointer',
                border: '1px solid rgba(6,182,212,0.4)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
              }}
            >
              <img
                src={getMediaUrl(video.featured_products[0].image_url)}
                alt=""
                style={{ width: '40px', height: '40px', borderRadius: '6px', objectFit: 'cover' }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '12px', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {video.featured_products[0].title}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                  {formatPrice(video.featured_products[0].price)} • {video.featured_products[0].merchant_city}
                </div>
              </div>
              <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                <ShoppingBag size={13} /> Buy
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
