import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, AlertTriangle, Layers, Tag, Plus, ShoppingBag, Sparkles, ExternalLink, Eye } from 'lucide-react';
import { api, getMediaUrl, formatPrice } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ProductModal } from '../components/ProductModal';

export const IngestPage: React.FC = () => {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);

  // Quick form for converting a detected object into a product listing
  const [selectedDetection, setSelectedDetection] = useState<any>(null);
  const [productPrice, setProductPrice] = useState(2499.0);
  const [productCategory, setProductCategory] = useState('Footwear & Sneakers');
  const [productAddedSuccess, setProductAddedSuccess] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      if (!title) {
        setTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setErrorMsg('');
    setUploadResult(null);

    try {
      const res = await api.uploadVideo(file, title, description);
      setUploadResult(res);
      if (res.recognized_category) {
        setProductCategory(res.recognized_category);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to process media.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateProductFromDetection = async () => {
    if (!selectedDetection) return;
    try {
      await api.createProduct({
        title: `${selectedDetection.label.toUpperCase()} — Listed from Video Frame`,
        description: `Authentic local item recognized via computer vision in video '${title}'.`,
        category: productCategory,
        price: productPrice,
        inventory: 15,
        image_url: getMediaUrl(selectedDetection.crop_path) || getMediaUrl(uploadResult.thumbnail_url) || 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600',
        tags: [selectedDetection.label, 'ai-tagged', 'local']
      });
      setProductAddedSuccess(true);
      setTimeout(() => setProductAddedSuccess(false), 4000);
      setSelectedDetection(null);
    } catch (err: any) {
      alert(err.message || 'Error creating product');
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px 40px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
          AI Video <span className="text-gradient">Ingestion & Product Recognition</span>
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          Ingest short-form videos and photos. Ultralytics YOLOv11 scans frames, identifies product categories, extracts high-resolution crops, and retrieves ranked visually similar products using FAISS vector search.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(360px, 460px) 1fr', gap: '28px' }}>
        {/* Upload Form */}
        <div className="glass-panel" style={{ padding: '24px', height: 'fit-content' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UploadCloud size={18} color="var(--accent-cyan)" /> Upload New Media
          </h3>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Dropzone */}
            <div
              style={{
                border: '2px dashed rgba(255,255,255,0.15)',
                borderRadius: '12px',
                padding: '28px 16px',
                textAlign: 'center',
                background: 'rgba(0,0,0,0.2)',
                cursor: 'pointer'
              }}
              onClick={() => document.getElementById('mediaInput')?.click()}
            >
              <UploadCloud size={36} color="var(--accent-cyan)" style={{ margin: '0 auto 10px' }} />
              <div style={{ fontSize: '14px', fontWeight: 600 }}>
                {file ? file.name : 'Choose Video or Image to Process'}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Supports JPG, PNG, WebP, MP4, MOV (e.g. Red running shoes, Polo shirts, Casual shirts, Headphones)
              </div>
              <input
                id="mediaInput"
                type="file"
                accept="video/*,image/*"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>Title</label>
              <input
                className="input-field"
                placeholder="e.g. Red Athletic Sneakers Showcase"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>Description (Optional)</label>
              <textarea
                className="input-field"
                rows={3}
                placeholder="Context or details about the product demonstration..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {errorMsg && (
              <div style={{ padding: '10px 14px', borderRadius: '8px', background: 'rgba(239,68,68,0.15)', border: '1px solid #ef4444', color: '#f87171', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={16} /> {errorMsg}
              </div>
            )}

            <button type="submit" disabled={isUploading || !file} className="btn-primary" style={{ justifyContent: 'center', padding: '12px' }}>
              {isUploading ? (
                <>Processing Vision Pipeline & Extracting Similar Items...</>
              ) : (
                <>Run AI Recognition Pipeline</>
              )}
            </button>
          </form>
        </div>

        {/* Results & Detections Visualizer */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={18} color="var(--accent-purple)" /> Recognition Telemetry & Similar Products
          </h3>

          {uploadResult ? (
            <div>
              <div style={{ padding: '12px 16px', borderRadius: '10px', background: 'rgba(16,185,129,0.1)', border: '1px solid #10b981', color: '#34d399', fontSize: '13px', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={16} /> {uploadResult.message}
              </div>

              {/* Identified Category Badge */}
              <div style={{ marginBottom: '20px', padding: '14px 18px', borderRadius: '12px', background: 'linear-gradient(135deg, rgba(6,182,212,0.15), rgba(168,85,247,0.15))', border: '1px solid rgba(6,182,212,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Sparkles size={20} color="var(--accent-cyan)" />
                  <div>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-dim)', fontWeight: 700 }}>
                      Identified Product Category
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {uploadResult.recognized_category || 'General Footwear / Apparel'}
                      {uploadResult.confidence > 0 && (
                        <span style={{ fontSize: '12px', padding: '2px 8px', borderRadius: '12px', background: 'rgba(255,255,255,0.1)', color: 'var(--accent-cyan)' }}>
                          {Math.round(uploadResult.confidence * 100)}% Confidence
                        </span>
                      )}
                      {uploadResult.needs_review && (
                        <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', background: 'rgba(245,158,11,0.2)', color: '#fbbf24', border: '1px solid rgba(245,158,11,0.4)' }}>
                          Needs Review
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div style={{ padding: '4px 10px', borderRadius: '6px', background: 'rgba(6,182,212,0.2)', color: 'var(--accent-cyan)', fontSize: '12px', fontWeight: 700 }}>
                  FAISS Indexed
                </div>
              </div>

              {/* Detections List */}
              <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '10px' }}>
                Detected Visual Regions ({uploadResult.detections_count}):
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                {uploadResult.detections.map((det: any, idx: number) => (
                  <div
                    key={idx}
                    className="glass-card"
                    style={{
                      padding: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      borderLeft: '4px solid var(--accent-cyan)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      {det.crop_path ? (
                        <img
                          src={getMediaUrl(det.crop_path)}
                          alt={det.label}
                          style={{
                            width: '54px',
                            height: '54px',
                            borderRadius: '8px',
                            objectFit: 'cover',
                            border: '1px solid rgba(255,255,255,0.1)'
                          }}
                        />
                      ) : (
                        <div style={{
                          width: '54px',
                          height: '54px',
                          borderRadius: '8px',
                          background: 'rgba(255,255,255,0.05)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Tag size={20} color="var(--accent-cyan)" />
                        </div>
                      )}
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontWeight: 700, fontSize: '14px', textTransform: 'capitalize' }}>
                            {det.label}
                          </span>
                          <span style={{ fontSize: '11px', background: 'rgba(6,182,212,0.15)', color: '#38bdf8', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
                            {(det.confidence * 100).toFixed(1)}% Conf
                          </span>
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
                          Bounding Box: [{det.box.join(', ')}]
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => {
                          setSelectedDetection(det);
                          setProductCategory(det.recognized_category || det.label);
                        }}
                        className="btn-secondary"
                        style={{ fontSize: '11px', padding: '6px 10px' }}
                      >
                        <Plus size={13} /> List Item
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Visually Similar Products Section */}
              <div style={{ marginTop: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <ShoppingBag size={16} color="var(--accent-cyan)" /> Visually Similar Products in Catalogue
                  </div>
                  <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                    Ranked by multimodal visual embedding & color harmony
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '14px' }}>
                  {(uploadResult.similar_products || []).map((p: any) => (
                    <div
                      key={p.id}
                      className="glass-card"
                      style={{
                        padding: '12px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px',
                        cursor: 'pointer',
                        transition: 'transform 0.2s ease, border-color 0.2s ease',
                        border: '1px solid rgba(255,255,255,0.08)'
                      }}
                      onClick={() => setSelectedProductId(p.id)}
                    >
                      <div style={{ position: 'relative', width: '100%', height: '140px', borderRadius: '8px', overflow: 'hidden' }}>
                        <img
                          src={getMediaUrl(p.image_url)}
                          alt={p.title}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                        <div style={{ position: 'absolute', top: '8px', right: '8px', background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', color: 'var(--accent-cyan)', fontSize: '10px', fontWeight: 700, padding: '3px 7px', borderRadius: '4px', border: '1px solid rgba(6,182,212,0.4)' }}>
                          {p.match_percentage ? `${p.match_percentage}% Match` : `${Math.round(p.similarity_score * 100)}% Match`}
                        </div>
                      </div>

                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: '13px', fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {p.title}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
                          {p.merchant_name || p.merchant} • {p.merchant_city || 'Local'}
                        </div>
                        <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '6px' }}>
                          {formatPrice(p.price)}
                        </div>
                      </div>

                      <button
                        className="btn-primary"
                        style={{ padding: '6px 10px', fontSize: '11px', justifyContent: 'center' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedProductId(p.id);
                        }}
                      >
                        <Eye size={13} /> View Product
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Publish Detected Product Drawer */}
              {selectedDetection && (
                <div style={{ marginTop: '24px', padding: '18px', background: 'rgba(0,0,0,0.5)', borderRadius: '12px', border: '1px solid rgba(6,182,212,0.3)' }}>
                  <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '8px', color: 'var(--accent-cyan)' }}>
                    Publish Detected "{selectedDetection.label.toUpperCase()}" to Store
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
                    <div>
                      <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Price (INR)</label>
                      <input
                        type="number"
                        className="input-field"
                        value={productPrice}
                        onChange={(e) => setProductPrice(parseFloat(e.target.value) || 0)}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Category</label>
                      <input
                        className="input-field"
                        value={productCategory}
                        onChange={(e) => setProductCategory(e.target.value)}
                      />
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <button onClick={() => setSelectedDetection(null)} className="btn-secondary" style={{ fontSize: '11px' }}>Cancel</button>
                    <button onClick={handleCreateProductFromDetection} className="btn-primary" style={{ fontSize: '11px' }}>
                      <ShoppingBag size={13} /> Publish & Index in FAISS
                    </button>
                  </div>
                </div>
              )}

              {productAddedSuccess && (
                <div style={{ marginTop: '14px', padding: '10px', borderRadius: '8px', background: 'rgba(16,185,129,0.15)', color: '#34d399', fontSize: '12px', textAlign: 'center' }}>
                  ✓ Product listed and indexed into FAISS vector database!
                </div>
              )}
            </div>
          ) : (
            <div style={{ padding: '80px 20px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '13px' }}>
              Upload a product video or photo on the left to run Ultralytics YOLOv11 bounding boxes and retrieve ranked visually similar products from local merchants.
            </div>
          )}
        </div>
      </div>

      {/* Product Detail Modal */}
      <ProductModal productId={selectedProductId} onClose={() => setSelectedProductId(null)} />
    </div>
  );
};

