import React from "react";
import SymbolSelector from "../components/SymbolSelector";
import ExpirySelector from "../components/ExpirySelector";

const SelectorContainer = ({ symbol, onSymbolChange, onExpiryChange }) => {
  return (
    <div style={{
      padding: "1rem",
      fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif",
      backgroundColor: "#ffffff",
      borderRadius: "8px",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
      display: "flex",
      gap: "1.5rem",
      justifyContent: "flex-start",
      flexWrap: "wrap",
    }}>
      <style>
        {`
          @media (max-width: 768px) {
            .selector-container {
              flex-direction: column;
              gap: 1rem;
            }
          }
        `}
      </style>
      <div className="selector-container">
        <SymbolSelector value={symbol} onChange={onSymbolChange} />
        <ExpirySelector symbol={symbol} onChange={onExpiryChange} />
      </div>
    </div>
  );
};

export default SelectorContainer;