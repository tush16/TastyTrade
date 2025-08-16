import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ExpirySelector = ({ symbol, onChange }) => {
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
          headers: { 'Content-Type': 'application/json' }
        });
        setExpiryMap(response.data || {});
      } catch (err) {
        console.error("Failed to fetch expiries with symbols", err);
        setError("Failed to load expiry dates. Please try again.");
        setExpiryMap({});
      } finally {
        setLoading(false);
      }
    };

    fetchExpiryMap();
  }, [symbol]);

  const expiryDates = Object.keys(expiryMap).sort();

  return (
    <div style={{
      fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif",
    }}>
      <style>
        {`
          .expiry-selector {
            width: 100%;
            max-width: 200px;
            padding: 10px 12px;
            border-radius: 6px;
            border: 1.5px solid #e5e7eb;
            font-size: 14px;
            color: #1f2937;
            background-color: #ffffff;
            cursor: pointer;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
          }
          .expiry-selector:disabled {
            background-color: #f9fafb;
            cursor: not-allowed;
            opacity: 0.7;
          }
          .expiry-selector:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            outline: none;
          }
          .expiry-selector:hover:not(:disabled) {
            border-color: #2563eb;
          }
          .expiry-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 16px;
            color: #1f2937;
          }
          .loading-state, .error-state {
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            font-size: 14px;
            margin: 8px 0;
            max-width: 200px;
          }
          .loading-state {
            background: linear-gradient(to right, #f3f4f6, #ffffff);
            color: #4b5563;
            position: relative;
            overflow: hidden;
          }
          .loading-state::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
              90deg,
              transparent,
              rgba(255, 255, 255, 0.3),
              transparent
            );
            animation: shimmer 1.5s infinite;
          }
          .error-state {
            background-color: rgba(254, 226, 226, 0.2);
            color: #b91c1c;
            border: 1px solid #fecaca;
          }
          @keyframes shimmer {
            100% { left: 100%; }
          }
          @media (max-width: 768px) {
            .expiry-selector {
              font-size: 12px;
              padding: 8px 10px;
              max-width: 100%;
            }
            .expiry-label {
              font-size: 14px;
            }
            .loading-state, .error-state {
              font-size: 12px;
              padding: 10px;
              max-width: 100%;
            }
          }
        `}
      </style>

      {loading ? (
        <div className="loading-state">
          Loading expiries...
        </div>
      ) : error ? (
        <div className="error-state">
          {error}
        </div>
      ) : (
        <div>
          <label htmlFor="expiry-select" className="expiry-label">
            Select Expiry:
          </label>
          <select
            id="expiry-select"
            className="expiry-selector"
            onChange={(e) => {
              const selectedExpiry = e.target.value;
              onChange({
                expiry: selectedExpiry,
                optionSymbols: expiryMap[selectedExpiry] || []
              });
            }}
            disabled={expiryDates.length === 0}
          >
            <option value="">
              {expiryDates.length ? "-- Select Expiry --" : "-- No expiries available --"}
            </option>
            {expiryDates.map((expiry) => (
              <option key={expiry} value={expiry}>
                {new Date(expiry).toLocaleDateString('en-US', {
                  month: 'short',
                  day: '2-digit',
                  year: 'numeric'
                })}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
};

export default ExpirySelector;