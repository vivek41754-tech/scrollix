import React, { useState, useEffect, useRef } from 'react';
import { 
  MapPin, 
  Navigation, 
  Compass, 
  ShieldCheck, 
  Phone, 
  Store, 
  List, 
  Map as MapIcon, 
  Sliders, 
  AlertTriangle, 
  Loader2, 
  RefreshCw, 
  Globe, 
  CheckCircle2,
  ExternalLink,
  Sparkles
} from 'lucide-react';
import { Merchant } from '../types';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const LocationPage: React.FC = () => {
  const { location, setLocation, detectDeviceLocation, setManualLocation } = useAuth();
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [cities, setCities] = useState<any[]>([]);
  const [radiusKm, setRadiusKm] = useState(25);
  const [nearestDistanceKm, setNearestDistanceKm] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [seedingDemo, setSeedingDemo] = useState(false);
  const [seedNotice, setSeedNotice] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  const [selectedMerchant, setSelectedMerchant] = useState<Merchant | null>(null);

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const leafletMapRef = useRef<any>(null);

  // Fetch preset cities from backend
  useEffect(() => {
    api.getPresetCities().then((cts) => {
      setCities([
        { city: 'All Cities', latitude: 20.5937, longitude: 78.9629 },
        ...(cts || [])
      ]);
    }).catch(console.error);
  }, []);

  // Fetch nearby merchants whenever location or search radius changes
  useEffect(() => {
    loadNearbyMerchants();
  }, [location.lat, location.lng, location.city, radiusKm]);

  const loadNearbyMerchants = async () => {
    setLoading(true);
    try {
      if (location.city === 'All Cities') {
        const all = await api.getMerchants();
        setMerchants(all || []);
        setNearestDistanceKm(null);
      } else if (location.lat !== null && location.lng !== null) {
        const data = await api.getNearbyMerchants(location.lat, location.lng, radiusKm);
        setMerchants(data.merchants || []);
        setNearestDistanceKm(data.nearest_distance_km ?? null);
      } else {
        setMerchants([]);
        setNearestDistanceKm(null);
      }
    } catch (err) {
      console.error('Failed to load nearby merchants:', err);
      setMerchants([]);
      setNearestDistanceKm(null);
    } finally {
      setLoading(false);
    }
  };

  // Initialize and update Leaflet Map
  useEffect(() => {
    if (viewMode !== 'map' || !mapContainerRef.current) return;

    const L = (window as any).L;
    if (!L) return;

    const hasValidCoords = location.lat !== null && location.lng !== null;
    const initialCenter = hasValidCoords ? [location.lat, location.lng] : [20.5937, 78.9629];
    const initialZoom = hasValidCoords ? 13 : 4;

    if (!leafletMapRef.current) {
      const map = L.map(mapContainerRef.current).setView(initialCenter, initialZoom);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);
      leafletMapRef.current = map;
    }

    const map = leafletMapRef.current;

    // Clear existing markers & overlays
    map.eachLayer((layer: any) => {
      if (layer instanceof L.Marker || layer instanceof L.Circle || layer instanceof L.CircleMarker) {
        map.removeLayer(layer);
      }
    });

    if (hasValidCoords) {
      map.setView([location.lat, location.lng], 13);

      // Add User Location Pin & Radius Circle
      L.circleMarker([location.lat, location.lng], {
        radius: 9,
        fillColor: location.isDeviceLocation ? '#10b981' : '#38bdf8',
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.95
      }).addTo(map).bindPopup(`
        <div style="font-family: sans-serif; color: #111;">
          <strong style="font-size: 13px;">${location.isDeviceLocation ? '🛰️ Current Device Location' : '📍 Selected Location'}</strong><br/>
          <span style="font-size: 12px; color: #444;">${location.city}</span><br/>
          <span style="font-size: 11px; color: #777;">(${location.lat?.toFixed(4)}, ${location.lng?.toFixed(4)})</span>
        </div>
      `);

      L.circle([location.lat, location.lng], {
        radius: radiusKm * 1000,
        color: location.isDeviceLocation ? '#10b981' : '#06b6d4',
        weight: 1.5,
        fillColor: location.isDeviceLocation ? '#10b981' : '#06b6d4',
        fillOpacity: 0.08
      }).addTo(map);
    } else if (merchants.length > 0) {
      // Fit bounds to merchants when in All Cities mode
      try {
        const bounds = L.latLngBounds(merchants.map(m => [m.latitude, m.longitude]));
        map.fitBounds(bounds, { padding: [40, 40] });
      } catch {}
    }

    // Add Merchant Markers
    merchants.forEach((m) => {
      const marker = L.marker([m.latitude, m.longitude]).addTo(map);
      const isDemo = m.business_name.startsWith('[Demo]');
      marker.bindPopup(`
        <div style="font-family: sans-serif; color: #111; min-width: 190px;">
          ${isDemo ? '<div style="font-size: 10px; color: #ec4899; font-weight: bold; margin-bottom: 2px;">⚡ DEMO MERCHANT (10-20 KM)</div>' : ''}
          <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 700;">${m.business_name}</h4>
          <p style="margin: 0 0 6px 0; font-size: 12px; color: #555;">${m.category} • ${m.distance_km !== undefined ? m.distance_km + ' km away' : m.city}</p>
          <div style="font-size: 11px; color: #10b981; font-weight: bold; margin-bottom: 4px;">Trust Score: ${m.trust_score}%</div>
          <div style="font-size: 11px; color: #666;">${m.address || m.city}</div>
        </div>
      `);
      marker.on('click', () => setSelectedMerchant(m));
    });
  }, [viewMode, merchants, location.lat, location.lng, location.city, location.isDeviceLocation, radiusKm]);

  const handleCityChange = (cityName: string) => {
    if (cityName === 'All Cities') {
      setLocation({ lat: null, lng: null, city: 'All Cities', source: 'manual' });
      return;
    }
    const found = cities.find((c) => c.city === cityName);
    if (found) {
      setManualLocation(found.latitude, found.longitude, found.city);
    }
  };

  const handleDetectLocation = async () => {
    await detectDeviceLocation();
  };

  const handleSeedNearbyDemo = async () => {
    if (location.lat === null || location.lng === null || location.city === 'All Cities') {
      alert('Reference coordinates required: Please detect device location or select a specific city first to anchor 3 nearby demo merchants (10–20 km).');
      return;
    }
    setSeedingDemo(true);
    setSeedNotice(null);
    try {
      const res = await api.seedNearbyDemoMerchants(location.lat, location.lng, location.city);
      setSeedNotice(res.message || `Anchored 3 demo merchants 10–20 km from ${location.city}!`);
      await loadNearbyMerchants();
      setTimeout(() => setSeedNotice(null), 6000);
    } catch (err: any) {
      alert(err.message || 'Failed to seed nearby demo merchants');
    } finally {
      setSeedingDemo(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px 40px' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
            Location-Aware <span className="text-gradient">Commerce Discovery</span>
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Dynamic device-based geolocation & spherical Haversine proximity calculations connecting you to local verified merchants.
          </p>
        </div>

        {/* View Toggle */}
        <div style={{ display: 'flex', gap: '8px', background: 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '10px' }}>
          <button
            onClick={() => setViewMode('map')}
            style={{
              padding: '6px 14px',
              borderRadius: '8px',
              border: 'none',
              background: viewMode === 'map' ? 'var(--accent-blue)' : 'transparent',
              color: 'white',
              fontSize: '12px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer'
            }}
          >
            <MapIcon size={14} /> Map View
          </button>
          <button
            onClick={() => setViewMode('list')}
            style={{
              padding: '6px 14px',
              borderRadius: '8px',
              border: 'none',
              background: viewMode === 'list' ? 'var(--accent-blue)' : 'transparent',
              color: 'white',
              fontSize: '12px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer'
            }}
          >
            <List size={14} /> List View
          </button>
        </div>
      </div>

      {/* Permission / Status Alert Banner if error exists */}
      {location.errorMsg && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '10px',
          padding: '12px 16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#fca5a5', fontSize: '13px' }}>
            <AlertTriangle size={18} color="#ef4444" />
            <span><strong>Device Location Status:</strong> {location.errorMsg}</span>
          </div>
          <button
            onClick={handleDetectLocation}
            className="btn-secondary"
            style={{ padding: '6px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCw size={12} /> Retry Detection
          </button>
        </div>
      )}

      {/* Location Control Bar */}
      <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {/* Active Location Indicator Pill */}
          {location.status === 'detecting' ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '8px', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#38bdf8', fontSize: '12px', fontWeight: 600 }}>
              <Loader2 size={14} className="animate-spin" /> Detecting device coordinates...
            </div>
          ) : location.isDeviceLocation ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#34d399', fontSize: '12px', fontWeight: 600 }}>
              <Navigation size={14} color="#10b981" />
              <span>Device GPS: <strong>{location.city}</strong></span>
              <span style={{ fontSize: '11px', color: '#6ee7b7' }}>({location.lat?.toFixed(3)}, {location.lng?.toFixed(3)})</span>
            </div>
          ) : location.source === 'manual' ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.12)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#93c5fd', fontSize: '12px', fontWeight: 600 }}>
              <MapPin size={14} color="#60a5fa" />
              <span>Manual: <strong>{location.city}</strong></span>
              {location.lat !== null && <span style={{ fontSize: '11px', color: '#bfdbfe' }}>({location.lat?.toFixed(3)}, {location.lng?.toFixed(3)})</span>}
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '8px', background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.3)', color: '#fcd34d', fontSize: '12px', fontWeight: 600 }}>
              <MapPin size={14} color="#f59e0b" />
              <span>Location Not Set</span>
            </div>
          )}

          {/* Detect Device Location Button */}
          <button
            onClick={handleDetectLocation}
            disabled={location.status === 'detecting'}
            className="btn-primary"
            style={{
              padding: '8px 14px',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: location.status === 'detecting' ? 'wait' : 'pointer'
            }}
          >
            {location.status === 'detecting' ? (
              <>
                <Loader2 size={13} className="animate-spin" /> Detecting...
              </>
            ) : (
              <>
                <Navigation size={13} /> Detect Device Location
              </>
            )}
          </button>

          {/* City Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>or choose:</span>
            <select
              value={location.city}
              onChange={(e) => handleCityChange(e.target.value)}
              style={{
                background: 'rgba(0,0,0,0.5)',
                border: '1px solid rgba(255,255,255,0.15)',
                color: 'white',
                padding: '8px 12px',
                borderRadius: '8px',
                fontSize: '12px',
                outline: 'none'
              }}
            >
              {cities.map((c) => (
                <option key={c.city} value={c.city} style={{ background: '#111827' }}>
                  {c.city}
                </option>
              ))}
            </select>
          </div>

          {/* Seed 3 Nearby Demo Merchants Button */}
          {location.lat !== null && location.lng !== null && location.city !== 'All Cities' && (
            <button
              onClick={handleSeedNearbyDemo}
              disabled={seedingDemo}
              title="Seed 3 clearly labelled demo merchants 10–20 km from this location"
              style={{
                padding: '7px 12px',
                borderRadius: '8px',
                border: '1px solid rgba(236, 72, 153, 0.4)',
                background: 'rgba(236, 72, 153, 0.12)',
                color: '#f472b6',
                fontSize: '12px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: seedingDemo ? 'wait' : 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {seedingDemo ? (
                <>
                  <Loader2 size={13} className="animate-spin" /> Seeding...
                </>
              ) : (
                <>
                  <Sparkles size={13} /> Seed 3 Nearby Demo (10–20 km)
                </>
              )}
            </button>
          )}
        </div>

        {/* Radius Filter & Distance Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Radius:</span>
            <strong style={{ fontSize: '13px', color: 'var(--accent-cyan)' }}>{radiusKm} km</strong>
            <input
              type="range"
              min="2"
              max="100"
              value={radiusKm}
              onChange={(e) => setRadiusKm(parseInt(e.target.value))}
              style={{ width: '110px', accentColor: 'var(--accent-cyan)' }}
            />
          </div>

          {/* Radius Quick Chips */}
          <div style={{ display: 'flex', gap: '4px' }}>
            {[5, 15, 25, 50].map((rk) => (
              <button
                key={rk}
                onClick={() => setRadiusKm(rk)}
                style={{
                  padding: '3px 8px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.1)',
                  background: radiusKm === rk ? 'rgba(6, 182, 212, 0.25)' : 'rgba(255,255,255,0.03)',
                  color: radiusKm === rk ? '#67e8f9' : 'var(--text-muted)',
                  fontSize: '11px',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                {rk}k
              </button>
            ))}
          </div>

          <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
            ({loading ? '...' : `${merchants.length} found`})
          </span>
        </div>
      </div>

      {/* Seed Notice Banner */}
      {seedNotice && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: '10px',
          padding: '10px 16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: '#34d399',
          fontSize: '13px',
          fontWeight: 500
        }}>
          <CheckCircle2 size={16} />
          <span>{seedNotice}</span>
        </div>
      )}

      {/* Main Content Area */}
      {viewMode === 'map' ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: '24px', height: '620px' }}>
          {/* OpenStreetMap Container */}
          <div className="glass-panel" style={{ padding: '8px', height: '100%', overflow: 'hidden' }}>
            <div ref={mapContainerRef} style={{ width: '100%', height: '100%', borderRadius: '12px' }} />
          </div>

          {/* Sidebar Nearby Merchants List */}
          <div className="glass-panel" style={{ padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 700 }}>Nearby Merchants</h4>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{merchants.length} within {radiusKm} km</span>
            </div>

            {loading ? (
              <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 12px' }} />
                <p style={{ fontSize: '12px' }}>Calculating proximity to local merchants...</p>
              </div>
            ) : location.lat === null && location.city !== 'All Cities' ? (
              /* Location Unset Empty State */
              <div style={{ padding: '24px 16px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px dashed rgba(255,255,255,0.1)' }}>
                <Compass size={32} color="#38bdf8" style={{ margin: '0 auto 12px', opacity: 0.8 }} />
                <h5 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '6px' }}>Device Location Required</h5>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px', lineHeight: 1.5 }}>
                  Detect your current device location or choose a demo city to discover nearby merchants.
                </p>
                <button
                  onClick={handleDetectLocation}
                  className="btn-primary"
                  style={{ width: '100%', padding: '8px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', marginBottom: '10px' }}
                >
                  <Navigation size={13} /> Detect My Location
                </button>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', justifyContent: 'center' }}>
                  {['Bengaluru', 'Mumbai', 'New Delhi', 'San Francisco'].map((c) => (
                    <button
                      key={c}
                      onClick={() => handleCityChange(c)}
                      style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.05)', color: 'white', fontSize: '11px', cursor: 'pointer' }}
                    >
                      {c}
                    </button>
                  ))}
                </div>
              </div>
            ) : merchants.length === 0 ? (
              /* Honest Empty State when no merchants are within radius */
              <div style={{ padding: '24px 16px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px dashed rgba(255,255,255,0.1)' }}>
                <Store size={32} color="#f59e0b" style={{ margin: '0 auto 12px', opacity: 0.8 }} />
                <h5 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '6px' }}>No Merchants Nearby</h5>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.5 }}>
                  No registered merchants found within <strong>{radiusKm} km</strong> of {location.city}.
                  {nearestDistanceKm !== null && (
                    <span style={{ display: 'block', marginTop: '6px', color: '#38bdf8' }}>
                      Nearest registered merchant is <strong>{nearestDistanceKm} km</strong> away.
                    </span>
                  )}
                </p>
                {nearestDistanceKm !== null && (
                  <button
                    onClick={() => setRadiusKm(Math.min(100, Math.ceil(nearestDistanceKm) + 5))}
                    className="btn-secondary"
                    style={{ width: '100%', padding: '8px 12px', fontSize: '12px', marginBottom: '12px' }}
                  >
                    Expand Radius to {Math.min(100, Math.ceil(nearestDistanceKm) + 5)} km
                  </button>
                )}
                <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '8px' }}>Or explore active demo hubs:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', justifyContent: 'center' }}>
                  {['Bengaluru', 'Mumbai', 'New Delhi', 'San Francisco'].map((c) => (
                    <button
                      key={c}
                      onClick={() => handleCityChange(c)}
                      style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.05)', color: 'white', fontSize: '11px', cursor: 'pointer' }}
                    >
                      {c}
                    </button>
                  ))}
                  <button
                    onClick={() => handleCityChange('All Cities')}
                    style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.3)', background: 'rgba(59,130,246,0.1)', color: '#93c5fd', fontSize: '11px', cursor: 'pointer' }}
                  >
                    View All Cities
                  </button>
                </div>
              </div>
            ) : (
              /* Merchant list */
              merchants.map((m) => (
                <div
                  key={m.id}
                  className="glass-card"
                  onClick={() => {
                    setSelectedMerchant(m);
                    if (leafletMapRef.current) {
                      leafletMapRef.current.setView([m.latitude, m.longitude], 15);
                    }
                  }}
                  style={{
                    padding: '12px',
                    cursor: 'pointer',
                    border: selectedMerchant?.id === m.id ? '1px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.06)',
                    background: selectedMerchant?.id === m.id ? 'rgba(6, 182, 212, 0.08)' : undefined
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700 }}>{m.business_name}</span>
                      {m.business_name.startsWith('[Demo]') && (
                        <span style={{ fontSize: '9px', background: 'rgba(236,72,153,0.18)', color: '#f472b6', padding: '1px 5px', borderRadius: '4px', fontWeight: 700, border: '1px solid rgba(236,72,153,0.35)', whiteSpace: 'nowrap' }}>DEMO (10-20 KM)</span>
                      )}
                    </div>
                    <span style={{ fontSize: '11px', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                      {m.distance_km !== undefined ? `${m.distance_km} km` : m.city}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>{m.category}</div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ fontSize: '11px', color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <ShieldCheck size={12} /> Trust: {m.trust_score}%
                    </div>
                    <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{m.products_count || 0} products</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      ) : (
        /* List Discovery Mode */
        <div>
          {merchants.length === 0 ? (
            <div className="glass-panel" style={{ padding: '40px 20px', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
              <Store size={48} color="#f59e0b" style={{ margin: '0 auto 16px', opacity: 0.8 }} />
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '8px' }}>No Merchants Within {radiusKm} km</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px', lineHeight: 1.6 }}>
                Scrollix AI strictly respects real-world physical proximity and never pretends merchants thousands of kilometers away are in your neighborhood.
                {nearestDistanceKm !== null && (
                  <span style={{ display: 'block', marginTop: '8px', color: 'var(--accent-cyan)' }}>
                    The closest registered merchant is <strong>{nearestDistanceKm} km</strong> from your detected location.
                  </span>
                )}
              </p>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
                {nearestDistanceKm !== null && (
                  <button
                    onClick={() => setRadiusKm(Math.min(100, Math.ceil(nearestDistanceKm) + 5))}
                    className="btn-primary"
                    style={{ padding: '8px 16px', fontSize: '13px' }}
                  >
                    Expand to {Math.min(100, Math.ceil(nearestDistanceKm) + 5)} km
                  </button>
                )}
                <button
                  onClick={() => handleCityChange('Bengaluru')}
                  className="btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '13px' }}
                >
                  Explore Bengaluru
                </button>
                <button
                  onClick={() => handleCityChange('Mumbai')}
                  className="btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '13px' }}
                >
                  Explore Mumbai
                </button>
                <button
                  onClick={() => handleCityChange('All Cities')}
                  className="btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '13px' }}
                >
                  View All Cities
                </button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
              {merchants.map((m) => (
                <div key={m.id} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ fontSize: '11px', padding: '3px 8px', borderRadius: '4px', background: 'rgba(59,130,246,0.15)', color: '#60a5fa', fontWeight: 600 }}>{m.category}</span>
                        {m.business_name.startsWith('[Demo]') && (
                          <span style={{ fontSize: '9.5px', background: 'rgba(236,72,153,0.18)', color: '#f472b6', padding: '1px 6px', borderRadius: '4px', fontWeight: 700, border: '1px solid rgba(236,72,153,0.35)', whiteSpace: 'nowrap' }}>DEMO (10-20 KM)</span>
                        )}
                      </div>
                      <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--accent-cyan)' }}>{m.distance_km !== undefined ? `${m.distance_km} km away` : m.city}</span>
                    </div>
                    <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>{m.business_name}</h3>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.5 }}>{m.description}</p>
                    <div style={{ fontSize: '12px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                      <MapPin size={13} /> {m.address || m.city}
                    </div>
                    {m.phone && (
                      <div style={{ fontSize: '12px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Phone size={13} /> {m.phone}
                      </div>
                    )}
                  </div>
                  <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '12px', color: '#34d399', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <ShieldCheck size={14} /> {m.trust_score}% Trust Score
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{m.products_count || 0} products listed</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
