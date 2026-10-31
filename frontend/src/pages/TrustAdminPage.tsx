import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle, XCircle, RefreshCw, Cpu, Database, HardDrive, Sparkles, AlertTriangle } from 'lucide-react';
import { FraudFlagItem, SystemHealth } from '../types';
import { api } from '../services/api';

export const TrustAdminPage: React.FC = () => {
  const [flags, setFlags] = useState<FraudFlagItem[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [flagsData, healthData] = await Promise.all([
        api.getFraudFlags(),
        api.getHealth()
      ]);
      setFlags(flagsData);
      setHealth(healthData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunScan = async () => {
    setScanning(true);
    try {
      await api.runFraudScan();
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setScanning(false);
    }
  };

  const handleResolveFlag = async (id: number, action: 'approved' | 'dismissed') => {
    try {
      await api.resolveFlag(id, action);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px 40px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
            Trust, Safety & <span className="text-gradient">System Telemetry</span>
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Explainable anomaly flags, merchant verification audits, and local AI model health monitor.
          </p>
        </div>

        <button onClick={handleRunScan} disabled={scanning} className="btn-primary">
          <RefreshCw size={16} className={scanning ? 'animate-spin' : ''} />
          {scanning ? 'Running Anomaly Audit...' : 'Run Fraud Audit Scan'}
        </button>
      </div>

      {/* System Health Telemetry Cards */}
      {health && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '18px', marginBottom: '32px' }}>
          {/* Computer Vision */}
          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Cpu size={20} color="var(--accent-cyan)" />
              <h4 style={{ fontSize: '14px', fontWeight: 700 }}>Computer Vision</h4>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Model: <strong>{health.computer_vision.model}</strong></div>
            <div style={{ fontSize: '12px', color: health.computer_vision.status === 'online' ? '#34d399' : '#fbbf24', marginTop: '4px' }}>
              Status: <strong>{health.computer_vision.status.toUpperCase()}</strong>
            </div>
          </div>

          {/* FAISS Vector DB */}
          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Sparkles size={20} color="var(--accent-purple)" />
              <h4 style={{ fontSize: '14px', fontWeight: 700 }}>FAISS Vector Search</h4>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Dimensions: <strong>{health.vector_search.vector_dimension}d (Unit Normal)</strong></div>
            <div style={{ fontSize: '12px', color: '#34d399', marginTop: '4px' }}>
              Indexed Catalogue: <strong>{health.vector_search.indexed_items_count} embeddings</strong>
            </div>
          </div>

          {/* Database */}
          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Database size={20} color="var(--accent-blue)" />
              <h4 style={{ fontSize: '14px', fontWeight: 700 }}>Database Storage</h4>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Engine: <strong>{health.database.type}</strong></div>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>
              {health.database.users_count} Users • {health.database.merchants_count} Merchants • {health.database.products_count} Products • {health.database.videos_count} Videos
            </div>
          </div>

          {/* Disk & Free Space */}
          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <HardDrive size={20} color="var(--accent-emerald)" />
              <h4 style={{ fontSize: '14px', fontWeight: 700 }}>Disk Storage</h4>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Free App Storage: <strong>{health.storage.free_space_gb} GB</strong></div>
            <div style={{ fontSize: '12px', color: '#34d399', marginTop: '4px' }}>Writable Local Directory Ready</div>
          </div>
        </div>
      )}

      {/* Fraud & Moderation Section */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={20} color="var(--accent-rose)" /> Explainable Fraud Flags for Review
        </h3>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '20px' }}>
          Flags are human-in-the-loop decision aids based on listing velocity, duplicate images, and extreme price outliers. Users are not banned automatically.
        </p>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading audit queue...</div>
        ) : flags.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {flags.map((f) => (
              <div
                key={f.id}
                className="glass-card"
                style={{
                  padding: '18px',
                  borderLeft: f.risk_score >= 60 ? '4px solid #ef4444' : '4px solid #f59e0b',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  gap: '20px'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '15px', fontWeight: 700 }}>{f.target_name}</span>
                    <span style={{ fontSize: '11px', textTransform: 'uppercase', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                      {f.target_type}
                    </span>
                    <span
                      style={{
                        fontSize: '11px',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: f.status === 'pending' ? 'rgba(245,158,11,0.2)' : f.status === 'approved' ? 'rgba(16,185,129,0.2)' : 'rgba(107,114,128,0.2)',
                        color: f.status === 'pending' ? '#fbbf24' : f.status === 'approved' ? '#34d399' : '#9ca3af',
                        fontWeight: 600
                      }}
                    >
                      {f.status.toUpperCase()}
                    </span>
                  </div>

                  {/* Risk Score */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Risk Score:</span>
                    <span style={{ fontSize: '13px', fontWeight: 800, color: f.risk_score >= 60 ? '#f87171' : '#fbbf24' }}>
                      {f.risk_score} / 100
                    </span>
                  </div>

                  {/* Bulleted Explainable Reasons */}
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                    <strong>Detected Anomaly Signals:</strong>
                    <ul style={{ paddingLeft: '18px', marginTop: '4px' }}>
                      {f.reasons.map((r, rIdx) => (
                        <li key={rIdx}>{r}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Admin Actions */}
                {f.status === 'pending' && (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => handleResolveFlag(f.id, 'approved')}
                      className="btn-secondary"
                      style={{ fontSize: '12px', padding: '8px 12px', color: '#34d399', borderColor: 'rgba(16,185,129,0.3)' }}
                    >
                      <CheckCircle size={14} /> Approve Verified
                    </button>
                    <button
                      onClick={() => handleResolveFlag(f.id, 'dismissed')}
                      className="btn-secondary"
                      style={{ fontSize: '12px', padding: '8px 12px', color: '#f87171', borderColor: 'rgba(239,68,68,0.3)' }}
                    >
                      <XCircle size={14} /> Dismiss Flag
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
            No suspicious fraud flags currently queued. All active merchants within standard variance thresholds.
          </div>
        )}
      </div>
    </div>
  );
};
