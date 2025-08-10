import React from "react";

const SymbolSelector = ({ value, onChange }) => {
  const symbols = ["META", "AAPL", "TSLA"];

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        padding: "8px 12px",
        borderRadius: "6px",
        border: "1.5px solid #ccc",
        fontSize: "1rem",
        cursor: "pointer",
        backgroundColor: "#fff",
        transition: "border-color 0.2s ease",
        minWidth: "140px",
      }}
      onFocus={(e) => (e.target.style.borderColor = "#007bff")}
      onBlur={(e) => (e.target.style.borderColor = "#ccc")}
    >
      {symbols.map((s) => (
        <option key={s} value={s}>
          {s}
        </option>
      ))}
    </select>
  );
};

export default SymbolSelector;
