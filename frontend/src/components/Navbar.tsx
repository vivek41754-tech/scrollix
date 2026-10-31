import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Search, 
  MapPin, 
  Bot, 
  Store, 
  ShieldAlert, 
  BarChart3, 
  UploadCloud, 
  Sparkles,
  Navigation,
  Loader2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import './Navbar.css';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const { user, switchRole, location } = useAuth();
  const [healthOk, setHealthOk] = useState(true);

  useEffect(() => {
    api.getHealth()
      .then((h) => setHealthOk(h.status === 'healthy'))
      .catch(() => setHealthOk(false));
    const interval = setInterval(() => {
      api.getHealth().then((h) => setHealthOk(h.status === 'healthy')).catch(() => setHealthOk(false));
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'feed', label: 'Video Feed', icon: Play },
    { id: 'ingest', label: 'AI Ingestion', icon: UploadCloud },
    { id: 'search', label: 'Smart Search', icon: Search },
    { id: 'location', label: 'Nearby Map', icon: MapPin },
    { id: 'assistant', label: 'AI Assistant', icon: Bot },
    { id: 'merchant', label: 'Merchant Hub', icon: Store },
    { id: 'trust', label: 'Trust & Admin', icon: ShieldAlert },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  const handleRoleClick = async (role: 'customer' | 'merchant' | 'admin') => {
    await switchRole(role);
    if (role === 'customer') {
      setActiveTab('feed');
    } else if (role === 'merchant') {
      setActiveTab('merchant');
    } else if (role === 'admin') {
      setActiveTab('trust');
    }
  };

  return (
    <header className="navbar-header glass-panel">
      {/* Brand */}
      <div className="navbar-brand" onClick={() => setActiveTab('feed')} title="Scrollix AI Home - Video Feed">
        <div className="navbar-logo-icon">
          <Sparkles size={18} color="white" />
        </div>
        <div className="navbar-brand-text">
          <div className="navbar-brand-title">
            <span className="brand-name">Scrollix<span className="brand-ai">AI</span></span>
            <span className="brand-version">v1.0</span>
          </div>
          <div className="navbar-brand-subtitle">Social Commerce Engine</div>
        </div>
      </div>

      {/* Middle Navigation Tabs (all 8 fully visible and clickable) */}
      <nav className="navbar-nav" aria-label="Main Navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-tab-btn ${isActive ? 'active' : ''}`}
              title={item.label}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon size={14} className="nav-tab-icon" />
              <span className="nav-tab-label">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Right Controls: Location, Health Status, Role Switcher */}
      <div className="navbar-controls">
        {/* Location Badge */}
        <div
          className="navbar-location-badge"
          onClick={() => setActiveTab('location')}
          title={location.isDeviceLocation ? "Using detected device GPS location. Click to view map." : "Click to view location and nearby merchants."}
        >
          {location.status === 'detecting' ? (
            <>
              <Loader2 size={12} className="animate-spin" color="#38bdf8" />
              <span style={{ color: '#7dd3fc' }}>Detecting...</span>
            </>
          ) : location.isDeviceLocation ? (
            <>
              <Navigation size={12} color="#10b981" />
              <span className="location-city-text">{location.city}</span>
              <span className="location-tag gps">GPS</span>
            </>
          ) : location.source === 'manual' ? (
            <>
              <MapPin size={12} color="#60a5fa" />
              <span className="location-city-text">{location.city}</span>
              <span className="location-tag manual">Manual</span>
            </>
          ) : (
            <>
              <MapPin size={12} color="#f59e0b" />
              <span style={{ color: '#fcd34d' }}>Set Location</span>
            </>
          )}
        </div>

        {/* Backend Health Dot */}
        <div 
          className="navbar-health-badge" 
          title={healthOk ? "Backend & Local AI Models Ready (Connected)" : "Connecting to Backend..."}
        >
          <div className={`health-dot ${healthOk ? 'online' : 'syncing'}`} />
          <span className="health-text" style={{ color: healthOk ? '#34d399' : '#f87171' }}>
            {healthOk ? 'LIVE' : 'SYNC'}
          </span>
        </div>

        {/* Role Switcher - Shopper, Merchant, Admin always visible simultaneously */}
        <div className="navbar-role-switcher" role="group" aria-label="Role Switcher">
          <button
            onClick={() => handleRoleClick('customer')}
            className={`role-btn role-shopper ${user?.role === 'customer' ? 'active' : ''}`}
            title="Switch to Shopper role and open Video Feed"
          >
            Shopper
          </button>
          <button
            onClick={() => handleRoleClick('merchant')}
            className={`role-btn role-merchant ${user?.role === 'merchant' ? 'active' : ''}`}
            title="Switch to Merchant role and open Merchant Hub"
          >
            Merchant
          </button>
          <button
            onClick={() => handleRoleClick('admin')}
            className={`role-btn role-admin ${user?.role === 'admin' ? 'active' : ''}`}
            title="Switch to Admin role and open Trust & Admin Console"
          >
            Admin
          </button>
        </div>
      </div>
    </header>
  );
};
