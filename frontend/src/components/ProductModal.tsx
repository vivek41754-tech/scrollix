import React, { useState, useEffect } from 'react';
import { X, Star, ShoppingBag, ShieldCheck, MapPin, Sparkles, Send, MessageSquare } from 'lucide-react';
import { api, getMediaUrl, formatPrice } from '../services/api';

interface ProductModalProps {
  productId: number | null;
  onClose: () => void;
}

export const ProductModal: React.FC<ProductModalProps> = ({ productId, onClose }) => {
  const [product, setProduct] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [purchased, setPurchased] = useState(false);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    setPurchased(false);
    api.getProduct(productId)
      .then((data) => {
        setProduct(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    // Record view interaction
    api.recordInteraction(productId, 'view', 5.0);
  }, [productId]);

  if (!productId) return null;

  const handleBuy = async () => {
    await api.recordInteraction(productId, 'purchase_intent', 10.0);
    setPurchased(true);
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setSubmittingReview(true);
    try {
      await api.addReview(productId, newRating, newComment);
      const updated = await api.getProduct(productId);
      setProduct(updated);
      setNewComment('');
    } finally {
      setSubmittingReview(false);
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '850px', maxHeight: '90vh', overflowY: 'auto', position: 'relative', border: '1px solid rgba(255,255,255,0.15)', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.7)' }}>
        {/* Close Button */}
        <button onClick={onClose} style={{ position: 'absolute', top: '16px', right: '16px', background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '50%', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', cursor: 'pointer', zIndex: 10 }}>
          <X size={20} />
        </button>

        {loading ? (
          <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading product details & sentiment insights...</div>
        ) : product ? (
          <div>
            {/* Top Product Hero */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '24px', padding: '24px', borderBottom: '1px solid var(--border-color)' }}>
              <div>
                <img
                  src={getMediaUrl(product.image_url)}
                  alt={product.title}
                  style={{ width: '100%', height: '320px', objectFit: 'cover', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', padding: '3px 10px', borderRadius: '20px', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', fontWeight: 600 }}>{product.category}</span>
                    {product.merchant_verified && (
                      <span style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', color: '#34d399', background: 'rgba(16,185,129,0.1)', padding: '2px 8px', borderRadius: '20px' }}>
                        <ShieldCheck size={13} /> Verified Merchant
                      </span>
                    )}
                  </div>
                  <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px' }}>{product.title}</h2>
                  <div style={{ fontSize: '26px', fontWeight: 800, color: 'var(--accent-cyan)', marginBottom: '14px' }}>{formatPrice(product.price)}</div>
                  <p style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '16px', lineHeight: 1.6 }}>{product.description}</p>
                  
                  {/* Merchant card */}
                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', marginBottom: '16px' }}>
                    <div style={{ fontSize: '13px', fontWeight: 600 }}>Sold by: {product.merchant_name}</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                      <MapPin size={12} /> {product.merchant_city} • Trust Score: <strong style={{ color: '#34d399' }}>{product.merchant_trust_score}%</strong>
                    </div>
                  </div>
                </div>

                <div>
                  {purchased ? (
                    <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(16,185,129,0.15)', border: '1px solid #10b981', color: '#34d399', fontWeight: 600, textAlign: 'center' }}>
                      ✓ Order Placed! In-store pickup reserved at {product.merchant_name}.
                    </div>
                  ) : (
                    <button onClick={handleBuy} className="btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: '15px' }}>
                      <ShoppingBag size={18} /> Buy Now / Reserve for Pickup ({formatPrice(product.price)})
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Sentiment Analysis & Reviews Section */}
            <div style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <MessageSquare size={18} color="var(--accent-cyan)" /> Customer Feedback & Sentiment Analysis
                </h3>
                <span style={{ fontSize: '11px', color: 'var(--text-dim)', background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: '6px' }}>Local NLP Estimate</span>
              </div>

              {/* Sentiment Summary Card */}
              {product.sentiment_summary && (
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', marginBottom: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 600 }}>{product.sentiment_summary.summary}</span>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Average Polarity: <strong>{product.sentiment_summary.average_sentiment}</strong></span>
                  </div>

                  {/* Sentiment Bar */}
                  <div style={{ height: '8px', width: '100%', borderRadius: '4px', overflow: 'hidden', display: 'flex', background: '#374151' }}>
                    <div style={{ width: `${product.sentiment_summary.positive_pct}%`, background: '#10b981' }} title={`Positive: ${product.sentiment_summary.positive_pct}%`} />
                    <div style={{ width: `${product.sentiment_summary.neutral_pct}%`, background: '#6b7280' }} title={`Neutral: ${product.sentiment_summary.neutral_pct}%`} />
                    <div style={{ width: `${product.sentiment_summary.negative_pct}%`, background: '#ef4444' }} title={`Negative: ${product.sentiment_summary.negative_pct}%`} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-dim)', marginTop: '6px' }}>
                    <span style={{ color: '#34d399' }}>● {product.sentiment_summary.positive_pct}% Positive</span>
                    <span style={{ color: '#9ca3af' }}>● {product.sentiment_summary.neutral_pct}% Neutral</span>
                    <span style={{ color: '#f87171' }}>● {product.sentiment_summary.negative_pct}% Negative</span>
                  </div>
                </div>
              )}

              {/* Review list */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                {product.reviews && product.reviews.length > 0 ? (
                  product.reviews.map((r: any) => (
                    <div key={r.id} style={{ background: 'rgba(255,255,255,0.02)', padding: '12px 16px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.04)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600, fontSize: '13px' }}>{r.username}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '2px', color: '#fbbf24' }}>
                          {Array.from({ length: r.rating }).map((_, i) => (
                            <Star key={i} size={13} fill="#fbbf24" />
                          ))}
                        </div>
                      </div>
                      <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{r.comment}</p>
                      <div style={{ fontSize: '11px', color: r.sentiment_label === 'positive' ? '#34d399' : r.sentiment_label === 'negative' ? '#f87171' : '#9ca3af', marginTop: '4px' }}>
                        Sentiment: {r.sentiment_label} ({r.sentiment_score > 0 ? `+${r.sentiment_score}` : r.sentiment_score})
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ fontSize: '13px', color: 'var(--text-dim)', fontStyle: 'italic' }}>No customer reviews yet. Be the first to review!</div>
                )}
              </div>

              {/* Add Review Form */}
              <form onSubmit={handleSubmitReview} style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: 'rgba(0,0,0,0.3)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600 }}>Write a Review</span>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        size={18}
                        style={{ cursor: 'pointer', color: star <= newRating ? '#fbbf24' : '#4b5563' }}
                        fill={star <= newRating ? '#fbbf24' : 'none'}
                        onClick={() => setNewRating(star)}
                      />
                    ))}
                  </div>
                </div>
                <textarea
                  className="input-field"
                  rows={2}
                  placeholder="Share your experience (quality, fit, merchant service)..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
                <button type="submit" disabled={submittingReview} className="btn-secondary" style={{ alignSelf: 'flex-end', padding: '8px 16px', fontSize: '13px' }}>
                  <Send size={14} /> {submittingReview ? 'Analyzing...' : 'Post Review'}
                </button>
              </form>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
