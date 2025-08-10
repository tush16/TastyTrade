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
        return;
      }
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(`http://localhost:8000/option-chains`, {
          params: { symbol },
          headers: { 'Content-Type': 'application/json' }
        });

        // response.data is an object: { expiryDate: [optionSymbols...] }
        setExpiryMap(response.data || {});
      } catch (err) {
        console.error("Failed to fetch expiries with symbols", err);
        setError("Failed to load expiry dates");
        setExpiryMap({});
      } finally {
        setLoading(false);
      }
    };

    fetchExpiryMap();
  }, [symbol]);

  if (loading)
    return <div style={{ color: "#555", margin: "8px 0" }}>Loading expiries...</div>;

  if (error)
    return <div style={{ color: "red", margin: "8px 0" }}>{error}</div>;

  const expiryDates = Object.keys(expiryMap).sort();

  return (
    <div style={{ marginTop: 10 }}>
      <label
        htmlFor="expiry-select"
        style={{ display: "block", marginBottom: 6, fontWeight: "600", color: "#333" }}
      >
        Select Expiry:
      </label>
      <select
        id="expiry-select"
        onChange={(e) => {
          const selectedExpiry = e.target.value;
          onChange({
            expiry: selectedExpiry,
            optionSymbols: expiryMap[selectedExpiry] || []
          });
        }}
        disabled={expiryDates.length === 0}
        style={{
          padding: "8px 12px",
          borderRadius: 6,
          border: "1.5px solid #ccc",
          fontSize: "1rem",
          cursor: expiryDates.length === 0 ? "not-allowed" : "pointer",
          width: "200px",
          backgroundColor: expiryDates.length === 0 ? "#f9f9f9" : "#fff",
          transition: "border-color 0.2s ease",
        }}
        onFocus={(e) => (e.target.style.borderColor = "#007bff")}
        onBlur={(e) => (e.target.style.borderColor = "#ccc")}
      >
        <option value="">
          {expiryDates.length ? "-- Select Expiry --" : "-- No expiries available --"}
        </option>
        {expiryDates.map((expiry) => (
          <option key={expiry} value={expiry}>
            {new Date(expiry).toLocaleDateString()}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ExpirySelector;
