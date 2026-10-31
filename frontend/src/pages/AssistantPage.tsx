import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, Mic, MicOff, Key, Sparkles, AlertCircle, ShoppingBag, CheckCircle2 } from 'lucide-react';
import { api, getMediaUrl, formatPrice } from '../services/api';
import { ProductModal } from '../components/ProductModal';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  recommended_products?: any[];
  mode?: string;
  disclaimer?: string;
}

export const AssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      text: "Hello! I'm your Scrollix AI Shopping Assistant. How can I assist your local discovery today? You can ask for recommendations, budget constraints (e.g. 'find running sneakers under $150'), or compare items from local merchants.",
      disclaimer: "Using Scrollix Local AI Engine (No paid API required). Grounded in verified catalogue inventory."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);

  // Settings & Gemini Key
  const [showConfig, setShowConfig] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [configStatus, setConfigStatus] = useState<any>(null);
  const [keySavedMessage, setKeySavedMessage] = useState('');

  // Voice Recognition
  const [isListening, setIsListening] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getAssistantConfig().then(setConfigStatus).catch(console.error);
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    const newHistory = [...messages, { sender: 'user' as const, text: userMsg }];
    setMessages(newHistory);
    setLoading(true);

    try {
      const res = await api.chatAssistant(userMsg, messages);
      setMessages([
        ...newHistory,
        {
          sender: 'assistant',
          text: res.reply,
          recommended_products: res.recommended_products,
          mode: res.mode,
          disclaimer: res.disclaimer
        }
      ]);
    } catch (err: any) {
      setMessages([
        ...newHistory,
        {
          sender: 'assistant',
          text: "Sorry, I encountered an issue processing your query. Please try searching another category or adjust your request.",
          disclaimer: "Offline catalogue fallback error."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please use the typed input box.');
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
      setInput(transcript);
    };

    recognition.start();
  };

  const handleSaveApiKey = async () => {
    await api.setAssistantKey(apiKey);
    const updated = await api.getAssistantConfig();
    setConfigStatus(updated);
    setKeySavedMessage('API Key configuration updated successfully!');
    setTimeout(() => setKeySavedMessage(''), 3000);
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', padding: '0 20px 40px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.5px' }}>
            AI Shopping <span className="text-gradient">Assistant</span>
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Conversational product discovery grounded strictly in verified local merchant inventory.
          </p>
        </div>

        {/* Config Modal Toggle */}
        <button
          onClick={() => setShowConfig(!showConfig)}
          className="btn-secondary"
          style={{ fontSize: '12px', padding: '8px 14px' }}
        >
          <Key size={15} />
          <span>{configStatus?.gemini_configured ? 'Gemini API Configured' : 'Configure Gemini Key (Optional)'}</span>
        </button>
      </div>

      {/* Settings Drawer if open */}
      {showConfig && (
        <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px', border: '1px solid rgba(6,182,212,0.3)' }}>
          <h4 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '6px' }}>Optional Cloud LLM Settings</h4>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '14px' }}>
            Scrollix AI operates fully offline using the local catalogue assistant by default. You can optionally provide a free Google Gemini API key to enable cloud natural language responses.
          </p>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="password"
              className="input-field"
              placeholder="Paste GEMINI_API_KEY (optional)..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <button onClick={handleSaveApiKey} className="btn-primary" style={{ padding: '0 20px', whiteSpace: 'nowrap' }}>
              Save Key
            </button>
          </div>
          {keySavedMessage && (
            <div style={{ color: '#34d399', fontSize: '12px', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={14} /> {keySavedMessage}
            </div>
          )}
        </div>
      )}

      {/* Chat Area */}
      <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '620px', overflow: 'hidden' }}>
        {/* Messages Stream */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '82%',
                display: 'flex',
                gap: '12px'
              }}
            >
              {m.sender === 'assistant' && (
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg, #06b6d4, #3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Bot size={20} color="white" />
                </div>
              )}

              <div>
                <div
                  style={{
                    background: m.sender === 'user' ? 'linear-gradient(135deg, #0284c7, #2563eb)' : 'rgba(255,255,255,0.04)',
                    border: m.sender === 'user' ? 'none' : '1px solid rgba(255,255,255,0.08)',
                    borderRadius: m.sender === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                    padding: '14px 18px',
                    color: 'white',
                    fontSize: '14px',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {m.text}
                </div>

                {/* Grounded Product Recommendations Cards */}
                {m.recommended_products && m.recommended_products.length > 0 && (
                  <div style={{ marginTop: '12px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
                    {m.recommended_products.map((prod: any) => (
                      <div
                        key={prod.id}
                        className="glass-card"
                        onClick={() => setSelectedProductId(prod.id)}
                        style={{ padding: '10px', cursor: 'pointer', display: 'flex', gap: '10px', alignItems: 'center' }}
                      >
                        <img src={getMediaUrl(prod.image_url)} alt="" style={{ width: '48px', height: '48px', borderRadius: '8px', objectFit: 'cover' }} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: '12px', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {prod.title}
                          </div>
                          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                            {formatPrice(prod.price)}
                          </div>
                          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)' }}>
                            {prod.merchant}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Assistant Disclose Badge */}
                {m.disclaimer && (
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '6px', fontStyle: 'italic' }}>
                    {m.disclaimer}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '12px', alignItems: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              <Bot size={20} color="var(--accent-cyan)" /> Assistant is evaluating catalogue inventory & constraints...
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} style={{ padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.08)', background: 'rgba(0,0,0,0.3)', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <input
            className="input-field"
            placeholder="Ask about gifts under ₹2,000, sneakers in Bengaluru, or polo t-shirts..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            style={{ height: '46px' }}
          />

          <button
            type="button"
            onClick={handleVoiceInput}
            title="Voice input"
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
            {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          </button>

          <button type="submit" disabled={loading || !input.trim()} className="btn-primary" style={{ height: '46px', padding: '0 20px' }}>
            <Send size={16} />
          </button>
        </form>
      </div>

      <ProductModal
        productId={selectedProductId}
        onClose={() => setSelectedProductId(null)}
      />
    </div>
  );
};
