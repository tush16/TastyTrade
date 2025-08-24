import React from "react";

const SymbolSelector = ({ value, onChange }) => {
  const symbols = ["AAPL", "TSLA", "SMCI", "PLTR", "HOOD", "NVDA", "AMD", "GOOGL", "AMZN", "SPX", "RUT", "IWM", "XSP", "SPY", "QQQ"];

  return (
    <div style={{ fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif" }}>
      <style>
        {`
          .symbol-selector {
            width: 100%;
            max-width: 150px;
            padding: 10px 12px;
            border-radius: 6px;
            border: 1.5px solid #e5e7eb;
            font-size: 14px;
            color: #1f2937;
            background-color: #ffffff;
            cursor: pointer;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
          }
          .symbol-selector:disabled {
            background-color: #f9fafb;
            cursor: not-allowed;
            opacity: 0.7;
          }
          .symbol-selector:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            outline: none;
          }
          .symbol-selector:hover:not(:disabled) {
            border-color: #2563eb;
          }
          .symbol-label {
            display: block;
            margin-bottom: 4px;
            font-weight: 600;
            font-size: 14px;
            color: #1f2937;
          }
        `}
      </style>

      <div>
        <label htmlFor="symbol-select" className="symbol-label">
          Symbol:
        </label>
        <select
          id="symbol-select"
          className="symbol-selector"
          value={value || ""}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">-- Select Symbol --</option>
          {symbols.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default SymbolSelector;
