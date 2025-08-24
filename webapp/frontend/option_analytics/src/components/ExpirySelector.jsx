import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ExpirySelector = ({ symbol, selectedExpiry, onChange }) => {
  const [expiryMap, setExpiryMap] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExpiryMap = async () => {
      if (!symbol) {
        setExpiryMap({});
        setError(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`http://localhost:8000/option-chains`, {
          params: { symbol },
        });
        setExpiryMap(response.data || {});
      } catch (err) {
        console.error("Failed to fetch expiries", err);
        setError("Failed to load expiry dates.");
        setExpiryMap({});
      } finally {
        setLoading(false);
      }
    };
    fetchExpiryMap();
  }, [symbol]);

  const expiryDates = Object.keys(expiryMap).sort();

  const handleSelect = (expiry) => {
    onChange({ expiry, optionSymbols: expiryMap[expiry] || [] });
  };

  const daysToExpiry = (expiry) => {
    const today = new Date();
    const expDate = new Date(expiry);
    const diffTime = expDate - today;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  return (
    <div style={{ fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif'" }}>
      {loading ? (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '60px',
        }}>
          <div style={{
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #2563eb',
            borderRadius: '50%',
            width: '24px',
            height: '24px',
            animation: 'spin 1s linear infinite'
          }} />
          <span style={{ marginLeft: '8px', fontSize: '14px', color: '#2563eb' }}>
            Loading expiries...
          </span>
        </div>
      ) : error ? (
        <div style={{
          color: '#b91c1c',
          fontSize: '14px',
          textAlign: 'center',
          padding: '8px 0'
        }}>{error}</div>
      ) : (
        <div>
          <label style={{ marginBottom: '4px', display: 'block', fontWeight: 500 }}>Expiry:</label>
          {/* Scrollable container */}
          <div style={{
            display: 'flex',
            overflowX: 'auto',
            gap: '8px',
            paddingBottom: '8px',
            width: '100%',
            maxWidth: '800px',
            WebkitOverflowScrolling: 'touch',
          }}>
            {expiryDates.map((expiry) => (
              <div
                key={expiry}
                onClick={() => handleSelect(expiry)}
                style={{
                  minWidth: '120px',
                  flex: '0 0 auto',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: selectedExpiry === expiry ? '2px solid #2563eb' : '1.5px solid #e5e7eb',
                  backgroundColor: selectedExpiry === expiry ? '#e0f2ff' : '#fff',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  fontSize: '14px',
                }}
              >
                <span style={{ fontWeight: 600 }}>
                  {new Date(expiry).toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })}
                </span>
                <span style={{ fontSize: '12px', color: '#4b5563' }}>
                  {daysToExpiry(expiry)} days left
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Spinner animation */}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default ExpirySelector;
