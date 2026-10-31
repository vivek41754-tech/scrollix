import React, { useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { FeedPage } from './pages/FeedPage';
import { IngestPage } from './pages/IngestPage';
import { SearchPage } from './pages/SearchPage';
import { LocationPage } from './pages/LocationPage';
import { AssistantPage } from './pages/AssistantPage';
import { MerchantPortal } from './pages/MerchantPortal';
import { TrustAdminPage } from './pages/TrustAdminPage';
import { AnalyticsPage } from './pages/AnalyticsPage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('feed');

  return (
    <AuthProvider>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-primary)' }}>
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main style={{ flex: 1, padding: '10px 0' }}>
          {activeTab === 'feed' && <FeedPage />}
          {activeTab === 'ingest' && <IngestPage />}
          {activeTab === 'search' && <SearchPage />}
          {activeTab === 'location' && <LocationPage />}
          {activeTab === 'assistant' && <AssistantPage />}
          {activeTab === 'merchant' && <MerchantPortal />}
          {activeTab === 'trust' && <TrustAdminPage />}
          {activeTab === 'analytics' && <AnalyticsPage />}
        </main>
      </div>
    </AuthProvider>
  );
};

export default App;
