import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ExpirySelector = ({ symbol, onChange }) => {
  const [expiries, setExpiries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExpiries = async () => {
      if (!symbol) {
        setExpiries([]);
        return;
      }

      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.get(
          `http://localhost:8000/options/expiries`, 
          {
            params: { symbol },
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        // Ensure response is an array and format dates if needed
        const data = Array.isArray(response.data) ? response.data : [];
        setExpiries(data);
        
      } catch (err) {
        console.error("Failed to fetch expiries", err);
        setError("Failed to load expiry dates");
        setExpiries([]);
      } finally {
        setLoading(false);
      }
    };

    fetchExpiries();
  }, [symbol]);

  if (loading) return <div>Loading expiries...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="expiry-selector">
      <label>Select Expiry:</label>
      <select 
        onChange={(e) => onChange(e.target.value)} 
        disabled={expiries.length === 0}
      >
        <option value="">{expiries.length ? "-- Select Expiry --" : "-- No expiries available --"}</option>
        {expiries.map((expiry) => (
          <option key={expiry} value={expiry}>
            {new Date(expiry).toLocaleDateString()}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ExpirySelector;