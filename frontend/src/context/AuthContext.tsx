import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api } from '../services/api';

export interface LocationState {
  lat: number | null;
  lng: number | null;
  city: string;
  source: 'device' | 'manual' | 'unselected';
  status: 'idle' | 'detecting' | 'granted' | 'denied' | 'unavailable' | 'timeout' | 'unsupported';
  errorMsg: string | null;
  isDeviceLocation: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, pass: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  switchRole: (role: 'customer' | 'merchant' | 'admin') => Promise<void>;
  location: LocationState;
  setLocation: (loc: Partial<LocationState> | { lat: number | null; lng: number | null; city: string }) => void;
  detectDeviceLocation: () => Promise<void>;
  setManualLocation: (lat: number, lng: number, city: string) => void;
  clearLocation: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getSavedLocation = (): LocationState => {
  try {
    const raw = localStorage.getItem('scrollix_location');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed.city === 'string') {
        return {
          lat: typeof parsed.lat === 'number' ? parsed.lat : null,
          lng: typeof parsed.lng === 'number' ? parsed.lng : null,
          city: parsed.city,
          source: parsed.source || (parsed.isDeviceLocation ? 'device' : 'manual'),
          status: parsed.status || 'granted',
          errorMsg: null,
          isDeviceLocation: Boolean(parsed.isDeviceLocation || parsed.source === 'device')
        };
      }
    }
  } catch {}

  return {
    lat: null,
    lng: null,
    city: 'Location Unset',
    source: 'unselected',
    status: 'idle',
    errorMsg: null,
    isDeviceLocation: false
  };
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('scrollix_token'));
  const [location, setLocationState] = useState<LocationState>(getSavedLocation);

  const detectDeviceLocation = async (): Promise<void> => {
    setLocationState(prev => ({
      ...prev,
      status: 'detecting',
      errorMsg: null
    }));

    const applyLocation = async (lat: number, lng: number, fallbackCity?: string) => {
      let detectedCity = fallbackCity || 'Current device location';
      try {
        const geo = await api.reverseGeocode(lat, lng);
        if (geo && geo.city) {
          detectedCity = geo.city;
        }
      } catch (err) {
        console.warn('Reverse geocoding notice:', err);
        if (!fallbackCity) {
          detectedCity = `Location (${lat.toFixed(2)}, ${lng.toFixed(2)})`;
        }
      }

      const newLoc: LocationState = {
        lat,
        lng,
        city: detectedCity,
        source: 'device',
        status: 'granted',
        errorMsg: null,
        isDeviceLocation: true
      };

      setLocationState(newLoc);
      try {
        localStorage.setItem('scrollix_location', JSON.stringify(newLoc));
      } catch {}
    };

    const tryNetworkLocationFallback = async (): Promise<boolean> => {
      try {
        let locData: any = null;
        if (typeof window !== 'undefined' && (window as any).electronAPI?.getDeviceLocation) {
          locData = await (window as any).electronAPI.getDeviceLocation();
        }
        if (!locData || locData.error || !locData.latitude) {
          locData = await api.getDeviceLocation();
        }
        if (locData && locData.latitude && locData.longitude) {
          await applyLocation(locData.latitude, locData.longitude, locData.city);
          return true;
        }
      } catch (e) {
        console.warn('Device network geolocation fallback notice:', e);
      }
      return false;
    };

    // If running in packaged Electron desktop, use the desktop IPC / network geolocation bridge directly
    const isDesktopApp = typeof window !== 'undefined' && (
      Boolean((window as any).electronAPI) ||
      window.location.protocol === 'file:' ||
      window.location.protocol === 'app:' ||
      (typeof navigator !== 'undefined' && navigator.userAgent.toLowerCase().includes('electron'))
    );

    if (isDesktopApp) {
      const success = await tryNetworkLocationFallback();
      if (success) return;
    }

    // Try standard browser Geolocation API
    if (typeof window !== 'undefined' && navigator.geolocation) {
      const geoPromise = new Promise<boolean>((resolve) => {
        navigator.geolocation.getCurrentPosition(
          async (pos) => {
            await applyLocation(pos.coords.latitude, pos.coords.longitude);
            resolve(true);
          },
          async () => {
            // Geolocation API failed or unavailable, try network fallback
            const fallbackSuccess = await tryNetworkLocationFallback();
            resolve(fallbackSuccess);
          },
          {
            enableHighAccuracy: true,
            timeout: 6000,
            maximumAge: 60000
          }
        );
      });

      const outcome = await geoPromise;
      if (outcome) return;
    } else {
      const fallbackSuccess = await tryNetworkLocationFallback();
      if (fallbackSuccess) return;
    }

    // If all location detection methods failed, set clear honest error
    const privacyHelp = 'Could not detect device location. Please verify your Internet connection, check Windows Settings (Settings > Privacy & security > Location) to ensure Location access is turned On, or select a city manually.';
    setLocationState(prev => ({
      lat: prev.source === 'manual' ? prev.lat : null,
      lng: prev.source === 'manual' ? prev.lng : null,
      city: prev.source === 'manual' ? prev.city : 'Location Unset',
      source: prev.source === 'manual' ? 'manual' : 'unselected',
      status: 'unavailable',
      errorMsg: privacyHelp,
      isDeviceLocation: false
    }));
  };

  const setManualLocation = (lat: number, lng: number, city: string) => {
    const newLoc: LocationState = {
      lat,
      lng,
      city,
      source: 'manual',
      status: 'granted',
      errorMsg: null,
      isDeviceLocation: false
    };
    setLocationState(newLoc);
    try {
      localStorage.setItem('scrollix_location', JSON.stringify(newLoc));
    } catch {}
  };

  const clearLocation = () => {
    const resetLoc: LocationState = {
      lat: null,
      lng: null,
      city: 'Location Unset',
      source: 'unselected',
      status: 'idle',
      errorMsg: null,
      isDeviceLocation: false
    };
    setLocationState(resetLoc);
    try {
      localStorage.removeItem('scrollix_location');
    } catch {}
  };

  const setLocation = (loc: Partial<LocationState> | { lat: number | null; lng: number | null; city: string }) => {
    setLocationState(prev => {
      const updated: LocationState = {
        ...prev,
        ...loc,
        lat: loc.lat !== undefined ? loc.lat : prev.lat,
        lng: loc.lng !== undefined ? loc.lng : prev.lng,
        city: loc.city !== undefined ? loc.city : prev.city,
        source: (loc as any).source || ('lat' in loc && loc.lat !== null ? 'manual' : prev.source),
        isDeviceLocation: (loc as any).isDeviceLocation ?? ((loc as any).source === 'device')
      };
      try {
        localStorage.setItem('scrollix_location', JSON.stringify(updated));
      } catch {}
      return updated;
    });
  };

  useEffect(() => {
    // Attempt auto-login or load demo customer
    if (token) {
      api.getMe().then((u) => {
        if (u) setUser(u);
        else handleDefaultDemoLogin();
      }).catch(() => handleDefaultDemoLogin());
    } else {
      handleDefaultDemoLogin();
    }

    // Auto-detect device location on first launch if unset
    if (location.source === 'unselected' && location.status === 'idle') {
      detectDeviceLocation();
    }
  }, []);

  const handleDefaultDemoLogin = async () => {
    try {
      const res = await api.login('alex_shopper', 'customer123');
      localStorage.setItem('scrollix_token', res.access_token);
      setToken(res.access_token);
      setUser(res.user);
    } catch {
      // Offline fallback dummy user
      setUser({
        id: 1,
        username: 'alex_shopper',
        email: 'alex@gmail.com',
        role: 'customer'
      });
    }
  };

  const login = async (username: string, pass: string) => {
    const res = await api.login(username, pass);
    localStorage.setItem('scrollix_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const register = async (data: any) => {
    const res = await api.register(data);
    localStorage.setItem('scrollix_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem('scrollix_token');
    setToken(null);
    setUser(null);
  };

  const switchRole = async (role: 'customer' | 'merchant' | 'admin') => {
    try {
      const res = await api.demoSwitchRole(role);
      localStorage.setItem('scrollix_token', res.access_token);
      setToken(res.access_token);
      setUser(res.user);
    } catch (e) {
      console.warn('demoSwitchRole endpoint failed, attempting fallback credentials:', e);
      try {
        let targetUser = 'alex_shopper';
        let targetPass = 'customer123';
        if (role === 'merchant') {
          targetUser = 'pulse_kicks';
          targetPass = 'merchant123';
        } else if (role === 'admin') {
          targetUser = 'admin';
          targetPass = 'admin123';
        }
        await login(targetUser, targetPass);
      } catch (err) {
        console.warn('Fallback login failed, applying local demo user state:', err);
        const demoProfiles: Record<string, any> = {
          customer: { id: 5, username: 'alex_shopper', email: 'alex@gmail.com', role: 'customer', merchant_id: null },
          merchant: { id: 3, username: 'pulse_kicks', email: 'pulse@sneakers.com', role: 'merchant', merchant_id: 2 },
          admin: { id: 1, username: 'admin', email: 'admin@scrollix.ai', role: 'admin', merchant_id: null }
        };
        setUser(demoProfiles[role] || demoProfiles.customer);
      }
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      register,
      logout,
      switchRole,
      location,
      setLocation,
      detectDeviceLocation,
      setManualLocation,
      clearLocation
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
