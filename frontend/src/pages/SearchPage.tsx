import React, { useState, useEffect } from 'react';
import { Search, Mic, MicOff, Image as ImageIcon, Sparkles, Filter, MapPin, X } from 'lucide-react';
import { Product } from '../types';
import { api, getMediaUrl, formatPrice } from '../services/api';
import { ProductModal } from '../components/ProductModal';

export const SearchPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [maxPrice, setMaxPrice] = useState<number | undefined>(undefined);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);

  // Visual Image Search
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // Voice Search via Web Speech API
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);

  useEffect(() => {
    // Check Web Speech API support
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setSpeechSupported(!!SpeechRecognition);
    // Load initial products
    handleTextSearch('');
  }, []);

  const handleVoiceSearch = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser environment. Please use typed input.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setSearchQuery(transcript);
      handleTextSearch(transcript);
    };

    recognition.start();
  };

  const handleTextSearch = async (query = searchQuery) => {
    setLoading(true);
    try {
      if (imageFile) {
        // Run visual search
        const results = await api.searchVisual(imageFile, selectedCategory, undefined, maxPrice);
        setProducts(results);
      } else {
        const results = await api.searchText(query, selectedCategory, undefined, maxPrice);
        setProducts(results);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setImageFile(f);
      setImagePreview(URL.createObjectURL(f));
      // Auto run visual search
      setLoading(true);
      api.searchVisual(f, selectedCategory, undefined, maxPrice)
        .then((res) => setProducts(res))
        .finally(() => setLoading(false));
    }
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
    handleTextSearch(searchQuery);
  };

  const categories = ['All', 'Footwear & Sneakers', 'Electronics', 'Casual Shirts', 'Polo T-Shirts', 'Accessories', 'Home & Living'];

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px 40px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
          Multimodal <span className="text-gradient">AI Product Search</span>
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          Search catalogue by text, voice query, or upload an image to find visually similar products using FAISS vector search.
        </p>
      </div>

      {/* Search Input Bar */}
      <div className="glass-panel" style={{ padding: '18px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              className="input-field"
              placeholder={imageFile ? 'Searching by uploaded visual reference...' : 'Search sneakers, vintage leather bags, handmade ceramics...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleTextSearch()}
              disabled={!!imageFile}
              style={{ paddingLeft: '42px', height: '46px', fontSize: '15px' }}
            />
          </div>

          {/* Voice Search Mic Button */}
          {speechSupported && (
            <button
              onClick={handleVoiceSearch}
              title="Voice Search (Speech to text)"
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '10px',
                border: isListening ? '1px solid #f43f5e' : '1px solid rgba(255,255,255,0.12)',
                background: isListening ? 'rgba(244,63,94,0.2)' : 'rgba(255,255,255,0.06)',
                color: isListening ? '#f43f5e' : 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer'
              }}
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
          )}

          {/* Visual Image Search Button */}
          <button
            onClick={() => document.getElementById('visualSearchInput')?.click()}
            title="Visual Similarity Search by Image"
            style={{
              height: '46px',
              padding: '0 16px',
              borderRadius: '10px',
              border: imageFile ? '1px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.12)',
              background: imageFile ? 'rgba(6,182,212,0.15)' : 'rgba(255,255,255,0.06)',
              color: imageFile ? 'var(--accent-cyan)' : 'white',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <ImageIcon size={18} />
            <span>Visual Search</span>
          </button>
          <input
            id="visualSearchInput"
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleImageSelect}
          />

          <button onClick={() => handleTextSearch()} className="btn-primary" style={{ height: '46px', padding: '0 24px', fontSize: '14px' }}>
            Search
          </button>
        </div>

        {/* Uploaded Image Reference Pill */}
        {imagePreview && (
          <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(6,182,212,0.1)', padding: '6px 12px', borderRadius: '8px', border: '1px solid rgba(6,182,212,0.3)', width: 'fit-content' }}>
            <img src={imagePreview} alt="Reference" style={{ width: '28px', height: '28px', borderRadius: '4px', objectFit: 'cover' }} />
            <span style={{ fontSize: '12px', color: '#38bdf8', fontWeight: 600 }}>Visual Image Reference Active</span>
            <button onClick={clearImage} style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <X size={14} />
            </button>
          </div>
        )}

        {/* Filters Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          {/* Categories */}
          <div style={{ display: 'flex', gap: '8px' }}>
            {categories.map((c) => {
              const active = (c === 'All' && !selectedCategory) || selectedCategory === c;
              return (
                <button
                  key={c}
                  onClick={() => {
                    setSelectedCategory(c === 'All' ? '' : c);
                    setTimeout(() => handleTextSearch(), 50);
                  }}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '8px',
                    border: active ? '1px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.08)',
                    background: active ? 'rgba(6,182,212,0.15)' : 'rgba(255,255,255,0.02)',
                    color: active ? '#38bdf8' : 'var(--text-muted)',
                    fontSize: '12px',
                    fontWeight: active ? 600 : 500,
                    cursor: 'pointer'
                  }}
                >
                  {c}
                </button>
              );
            })}
          </div>

          {/* Budget Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
            <span>Max Price:</span>
            <input
              type="number"
              placeholder="e.g. 150"
              value={maxPrice ?? ''}
              onChange={(e) => setMaxPrice(e.target.value ? parseFloat(e.target.value) : undefined)}
              onBlur={() => handleTextSearch()}
              style={{
                width: '80px',
                padding: '4px 8px',
                borderRadius: '6px',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
        </div>
      </div>

      {/* Search Results Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          Computing CLIP embeddings & searching FAISS index...
        </div>
      ) : products.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '20px' }}>
          {products.map((p) => (
            <div
              key={p.id}
              className="glass-card"
              onClick={() => setSelectedProductId(p.id)}
              style={{ overflow: 'hidden', cursor: 'pointer', display: 'flex', flexDirection: 'column' }}
            >
              <div style={{ position: 'relative', width: '100%', height: '200px' }}>
                <img
                  src={getMediaUrl(p.image_url)}
                  alt={p.title}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                {p.similarity_score !== undefined && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '10px',
                      right: '10px',
                      background: 'rgba(0,0,0,0.75)',
                      backdropFilter: 'blur(4px)',
                      color: '#34d399',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontWeight: 700,
                      border: '1px solid rgba(16,185,129,0.3)'
                    }}
                  >
                    {Math.round(p.similarity_score * 100)}% Match
                  </div>
                )}
              </div>

              <div style={{ padding: '14px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#60a5fa', fontWeight: 600, marginBottom: '2px' }}>
                    {p.category}
                  </div>
                  <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '6px', lineHeight: 1.3 }}>
                    {p.title}
                  </h4>
                  <div style={{ fontSize: '12px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={11} /> {p.merchant_name} ({p.merchant_city})
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '12px' }}>
                  <span style={{ fontSize: '16px', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                    {formatPrice(p.price)}
                  </span>
                  <span style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', color: '#e5e7eb' }}>
                    View Details
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-muted)' }}>
          No catalogue products found matching your search. Try different keywords or upload a new photo.
        </div>
      )}

      <ProductModal
        productId={selectedProductId}
        onClose={() => setSelectedProductId(null)}
      />
    </div>
  );
};
