import React, { useState, useEffect } from 'react';
import { BarChart3, Eye, Heart, MousePointer, ShoppingBag, TrendingUp, Clock, Info } from 'lucide-react';
import { api } from '../services/api';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const res = await api.getAnalytics();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px 40px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
            Platform <span className="text-gradient">Engagement Analytics</span>
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Real-time business and interaction metrics calculated strictly from persisted database events.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-dim)', background: 'rgba(255,255,255,0.04)', padding: '6px 12px', borderRadius: '8px' }}>
          <Info size={14} /> Zero Synthetic Data • Live SQLite Engine
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '80px', textAlign: 'center', color: 'var(--text-muted)' }}>Aggregating event logs...</div>
      ) : data ? (
        <div>
          {/* Top KPI Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '18px', marginBottom: '28px' }}>
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600 }}>Total Views</span>
                <Eye size={18} color="var(--accent-blue)" />
              </div>
              <div style={{ fontSize: '26px', fontWeight: 800 }}>{data.summary.views}</div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>Dwell Time: ~{data.summary.average_dwell_time_sec}s avg</div>
            </div>

            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600 }}>Shopper Likes</span>
                <Heart size={18} color="var(--accent-rose)" />
              </div>
              <div style={{ fontSize: '26px', fontWeight: 800 }}>{data.summary.likes}</div>
              <div style={{ fontSize: '11px', color: '#f43f5e', marginTop: '4px' }}>Active social resonance</div>
            </div>

            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600 }}>Click-Through Rate (CTR)</span>
                <MousePointer size={18} color="var(--accent-cyan)" />
              </div>
              <div style={{ fontSize: '26px', fontWeight: 800, color: 'var(--accent-cyan)' }}>{data.summary.click_through_rate_pct}%</div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>{data.summary.clicks} product clicks</div>
            </div>

            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600 }}>Conversion Rate</span>
                <ShoppingBag size={18} color="var(--accent-emerald)" />
              </div>
              <div style={{ fontSize: '26px', fontWeight: 800, color: '#34d399' }}>{data.summary.conversion_rate_pct}%</div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>{data.summary.purchases} purchase intents</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '24px' }}>
            {/* 7-Day Activity Time-Series Chart */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>7-Day Interaction Activity</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '24px' }}>Daily distribution of video views, likes, and product clicks.</p>

              {/* Chart Bars */}
              <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', height: '220px', paddingBottom: '10px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                {data.time_series.map((day: any, i: number) => {
                  const maxDayVal = Math.max(...data.time_series.map((d: any) => Math.max(d.views, d.likes, d.clicks, 1)));
                  const viewHeight = Math.max(8, (day.views / maxDayVal) * 180);
                  const clickHeight = Math.max(4, (day.clicks / maxDayVal) * 180);

                  return (
                    <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', flex: 1 }}>
                      <div style={{ display: 'flex', gap: '4px', alignItems: 'flex-end', height: '180px' }}>
                        {/* Views Bar */}
                        <div
                          style={{
                            width: '14px',
                            height: `${viewHeight}px`,
                            background: 'linear-gradient(to top, #0284c7, #38bdf8)',
                            borderRadius: '4px 4px 0 0'
                          }}
                          title={`Views: ${day.views}`}
                        />
                        {/* Clicks Bar */}
                        <div
                          style={{
                            width: '14px',
                            height: `${clickHeight}px`,
                            background: 'linear-gradient(to top, #10b981, #34d399)',
                            borderRadius: '4px 4px 0 0'
                          }}
                          title={`Clicks: ${day.clicks}`}
                        />
                      </div>
                      <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{day.date}</span>
                    </div>
                  );
                })}
              </div>

              {/* Legend */}
              <div style={{ display: 'flex', gap: '16px', marginTop: '14px', fontSize: '12px', color: 'var(--text-muted)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: '10px', height: '10px', background: '#38bdf8', borderRadius: '2px' }} /> Views</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: '10px', height: '10px', background: '#34d399', borderRadius: '2px' }} /> Clicks</span>
              </div>
            </div>

            {/* Top Trending Products Leaderboard */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>Top Engaged Products</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '18px' }}>Ranked by aggregate shopper actions.</p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {data.top_products.map((p: any, idx: number) => (
                  <div
                    key={p.id}
                    className="glass-card"
                    style={{
                      padding: '12px 14px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 800, color: idx === 0 ? '#fbbf24' : 'var(--text-dim)', width: '20px' }}>#{idx + 1}</span>
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: 600 }}>{p.title}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{p.category} • ${p.price.toFixed(2)}</div>
                      </div>
                    </div>
                    <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                      {p.interactions_count} events
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
