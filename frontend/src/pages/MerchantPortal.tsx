import React, { useState, useEffect } from 'react';
import { 
  Store, 
  Plus, 
  ShieldCheck, 
  MapPin, 
  Trash2, 
  Package, 
  CheckCircle2, 
  Phone, 
  Sparkles, 
  Search, 
  ExternalLink,
  SlidersHorizontal
} from 'lucide-react';
import { Product, Merchant } from '../types';
import { api, getMediaUrl, formatPrice } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const MerchantPortal: React.FC = () => {
  const { user } = useAuth();
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [selectedMerchantId, setSelectedMerchantId] = useState<number | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  // New Product Modal Form
  const [showAddModal, setShowAddModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Footwear & Sneakers');
  const [price, setPrice] = useState(2499.0);
  const [inventory, setInventory] = useState(20);
  const [imageUrl, setImageUrl] = useState('https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600');
  const [tagsStr, setTagsStr] = useState('shoes, sneakers, athletic, streetwear');
  const [successMsg, setSuccessMsg] = useState('');

  // 1. Load All Merchants
  useEffect(() => {
    loadAllMerchants();
  }, []);

  const loadAllMerchants = async () => {
    setLoading(true);
    try {
      const allMerchants = await api.getMerchants();
      setMerchants(allMerchants || []);

      // Determine initial selected merchant
      const initialId = user?.merchant_id 
        ? user.merchant_id 
        : (allMerchants.length > 0 ? allMerchants[0].id : null);
      setSelectedMerchantId(initialId);
    } catch (err) {
      console.error('Error fetching merchants list:', err);
    } finally {
      setLoading(false);
    }
  };

  // 2. Load Products for Selected Merchant
  useEffect(() => {
    if (selectedMerchantId) {
      loadMerchantProducts(selectedMerchantId);
    }
  }, [selectedMerchantId]);

  const loadMerchantProducts = async (merchantId: number) => {
    setLoadingProducts(true);
    try {
      const prodData = await api.getProducts({ merchant_id: merchantId });
      setProducts(prodData || []);
    } catch (err) {
      console.error('Error fetching products for merchant:', err);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleSelectMerchant = (merchantId: number) => {
    setSelectedMerchantId(merchantId);
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMerchantId) {
      alert('Please select a merchant storefront first.');
      return;
    }

    try {
      const tags = tagsStr.split(',').map((t) => t.trim()).filter(Boolean);
      await api.createProduct({
        merchant_id: selectedMerchantId,
        title,
        description,
        category,
        price,
        inventory,
        image_url: imageUrl,
        tags
      });
      setShowAddModal(false);
      setSuccessMsg('Product created and indexed in FAISS vector engine!');
      setTimeout(() => setSuccessMsg(''), 4000);

      // Refresh products and merchant catalogue counts
      loadMerchantProducts(selectedMerchantId);
      const updatedMerchants = await api.getMerchants();
      setMerchants(updatedMerchants);

      // Reset form fields
      setTitle('');
      setDescription('');
    } catch (err: any) {
      alert(err.message || 'Failed to add product');
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      await api.deleteProduct(id);
      if (selectedMerchantId) {
        loadMerchantProducts(selectedMerchantId);
      }
      const updatedMerchants = await api.getMerchants();
      setMerchants(updatedMerchants);
    } catch (err: any) {
      alert(err.message || 'Failed to delete product');
    }
  };

  // Filtered merchants based on category and search
  const categoriesList = ['All', 'Footwear & Sneakers', 'Electronics', 'Casual Shirts', 'Polo T-Shirts', 'Accessories & Leathercraft', 'Home & Living'];
  
  const filteredMerchants = merchants.filter((m) => {
    const matchesCategory = selectedCategory === 'All' || m.category.toLowerCase().includes(selectedCategory.toLowerCase());
    const query = searchQuery.toLowerCase().trim();
    const matchesQuery = !query || 
      m.business_name.toLowerCase().includes(query) || 
      m.city.toLowerCase().includes(query) || 
      m.category.toLowerCase().includes(query) ||
      (m.description && m.description.toLowerCase().includes(query));
    return matchesCategory && matchesQuery;
  });

  const activeMerchant = merchants.find((m) => m.id === selectedMerchantId) || merchants[0];

  return (
    <div style={{ maxWidth: '1240px', margin: '0 auto', padding: '0 20px 40px' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
            Merchant <span className="text-gradient">Hub & Verified Storefronts</span>
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Directory of verified demo merchants with explainable trust scores, real stock inventory, and FAISS-indexed catalogues.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.3)', padding: '6px 14px', borderRadius: '8px', fontSize: '12px', color: 'var(--accent-cyan)', fontWeight: 600 }}>
            {merchants.length} Verified Merchants Available
          </div>
          <button onClick={() => setShowAddModal(true)} className="btn-primary" style={{ padding: '8px 16px', fontSize: '13px' }}>
            <Plus size={16} /> Add Product to Storefront
          </button>
        </div>
      </div>

      {successMsg && (
        <div style={{ padding: '12px 16px', borderRadius: '10px', background: 'rgba(16,185,129,0.15)', border: '1px solid #10b981', color: '#34d399', fontSize: '13px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={16} /> {successMsg}
        </div>
      )}

      {/* SECTION 1: VERIFIED MERCHANTS DIRECTORY (SHOWS ALL MERCHANTS) */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Store size={18} color="var(--accent-cyan)" /> Verified Merchant Directory ({filteredMerchants.length} shown)
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Click any merchant card to inspect its trust score and browse its live storefront inventory.
            </p>
          </div>

          {/* Search Box */}
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
            <input
              type="text"
              placeholder="Filter by merchant name or city..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field"
              style={{ paddingLeft: '36px', height: '36px', fontSize: '12px' }}
            />
          </div>
        </div>

        {/* Category Filter Pills */}
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '12px', marginBottom: '18px' }}>
          {categoriesList.map((cat) => {
            const active = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  padding: '5px 12px',
                  borderRadius: '8px',
                  border: active ? '1px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.08)',
                  background: active ? 'rgba(6,182,212,0.15)' : 'rgba(255,255,255,0.02)',
                  color: active ? '#38bdf8' : 'var(--text-muted)',
                  fontSize: '12px',
                  fontWeight: active ? 600 : 500,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* All Merchants Grid */}
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading verified merchants...</div>
        ) : filteredMerchants.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: '16px' }}>
            {filteredMerchants.map((m) => {
              const isSelected = selectedMerchantId === m.id;
              const productCount = m.product_count ?? m.products_count ?? 0;

              return (
                <div
                  key={m.id}
                  onClick={() => handleSelectMerchant(m.id)}
                  className="glass-card"
                  style={{
                    padding: '16px',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    border: isSelected ? '2px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.08)',
                    background: isSelected ? 'rgba(6,182,212,0.08)' : 'rgba(255,255,255,0.02)',
                    boxShadow: isSelected ? '0 0 16px rgba(6,182,212,0.25)' : 'none',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(59,130,246,0.15)', color: '#60a5fa', fontWeight: 600 }}>
                        {m.category}
                      </span>
                      {isSelected ? (
                        <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-cyan)', background: 'rgba(6,182,212,0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                          ✓ Active Storefront
                        </span>
                      ) : (
                        <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                          Click to view
                        </span>
                      )}
                    </div>

                    <h4 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {m.business_name}
                      {m.is_verified && <ShieldCheck size={14} color="#34d399" />}
                    </h4>

                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {m.description || 'Verified merchant offering curated quality products.'}
                    </p>

                    <div style={{ fontSize: '11.5px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                      <MapPin size={12} /> {m.city} • {m.address || 'Local Workshop'}
                    </div>

                    {m.phone && (
                      <div style={{ fontSize: '11.5px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Phone size={12} /> {m.phone}
                      </div>
                    )}
                  </div>

                  <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '11.5px', color: '#34d399', fontWeight: 600 }}>
                        Trust Score: {m.trust_score}%
                      </span>
                      <span style={{ fontSize: '11.5px', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                        {productCount} items
                      </span>
                    </div>

                    {/* Trust Score Progress Bar */}
                    <div style={{ height: '4px', width: '100%', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ width: `${m.trust_score}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)' }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-dim)' }}>
            No merchants found matching your filter criteria.
          </div>
        )}
      </div>

      {/* SECTION 2: ACTIVE STOREFRONT BANNER & DETAILS */}
      {activeMerchant && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px', border: '1px solid rgba(6,182,212,0.25)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <h2 style={{ fontSize: '22px', fontWeight: 700 }}>{activeMerchant.business_name}</h2>
                {activeMerchant.is_verified && (
                  <span style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', color: '#34d399', background: 'rgba(16,185,129,0.1)', padding: '2px 8px', borderRadius: '20px' }}>
                    <ShieldCheck size={13} /> Verified Merchant
                  </span>
                )}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.5 }}>
                {activeMerchant.description}
              </p>
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><MapPin size={13} /> {activeMerchant.address || activeMerchant.city}</span>
                <span>Category: <strong>{activeMerchant.category}</strong></span>
                {activeMerchant.phone && <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Phone size={13} /> {activeMerchant.phone}</span>}
              </div>
            </div>

            {/* Explainable Trust Score Box */}
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '18px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 600 }}>Merchant Trust Score</span>
                <span style={{ fontSize: '20px', fontWeight: 800, color: '#34d399' }}>{activeMerchant.trust_score}%</span>
              </div>
              <div style={{ height: '8px', width: '100%', background: '#374151', borderRadius: '4px', overflow: 'hidden', marginBottom: '8px' }}>
                <div style={{ width: `${activeMerchant.trust_score}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)' }} />
              </div>
              <p style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                Calculated locally from listing consistency, verified store location, and low dispute velocity.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 3: STOREFRONT PRODUCTS INVENTORY TABLE */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>
              Storefront Catalogue: {activeMerchant ? activeMerchant.business_name : ''} ({products.length} items)
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Products listed by this merchant in INR with live FAISS vector indexing.
            </p>
          </div>
        </div>

        {loadingProducts ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading products...</div>
        ) : products.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
            {products.map((p) => (
              <div key={p.id} className="glass-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <img src={getMediaUrl(p.image_url)} alt="" style={{ width: '100%', height: '180px', objectFit: 'cover', borderRadius: '10px', marginBottom: '12px' }} />
                  <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', fontWeight: 600 }}>{p.category}</div>
                  <h4 style={{ fontSize: '15px', fontWeight: 700, margin: '2px 0 6px' }}>{p.title}</h4>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px', lineHeight: 1.4 }}>{p.description}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                  <div>
                    <span style={{ fontSize: '16px', fontWeight: 800, color: 'white' }}>{formatPrice(p.price)}</span>
                    <span style={{ fontSize: '11px', color: 'var(--text-dim)', marginLeft: '8px' }}>Stock: {p.inventory}</span>
                  </div>
                  <button onClick={() => handleDeleteProduct(p.id)} style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', padding: '4px' }} title="Delete product">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
            No products listed for this merchant yet. Click "Add Product to Storefront" to list and index an item!
          </div>
        )}
      </div>

      {/* Add Product Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: '540px', padding: '24px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>
              Add New Product to {activeMerchant?.business_name}
            </h3>
            <form onSubmit={handleCreateProduct} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Title</label>
                <input className="input-field" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Vintage Denim Casual Shirt" required />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Description</label>
                <textarea className="input-field" rows={2} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe product materials and fit..." />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Category</label>
                  <select 
                    className="input-field" 
                    value={category} 
                    onChange={(e) => setCategory(e.target.value)}
                    style={{ background: '#111827', color: 'white' }}
                  >
                    <option value="Footwear & Sneakers">Footwear & Sneakers</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Casual Shirts">Casual Shirts</option>
                    <option value="Polo T-Shirts">Polo T-Shirts</option>
                    <option value="Accessories & Leathercraft">Accessories & Leathercraft</option>
                    <option value="Home & Living">Home & Living</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Price (₹)</label>
                  <input type="number" step="1" className="input-field" value={price} onChange={(e) => setPrice(parseFloat(e.target.value) || 0)} required />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Image URL (Unsplash)</label>
                <input className="input-field" value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Tags (comma-separated for semantic FAISS search)</label>
                <input className="input-field" value={tagsStr} onChange={(e) => setTagsStr(e.target.value)} />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '12px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary">Create & Index in FAISS</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
