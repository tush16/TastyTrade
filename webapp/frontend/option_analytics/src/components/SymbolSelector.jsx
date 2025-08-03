import React from "react";

const SymbolSelector = ({ value, onChange }) => {
  const symbols = ["META", "AAPL", "TSLA"];

  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {symbols.map((s) => (
        <option key={s} value={s}>
          {s}
        </option>
      ))}
    </select>
  );
};

export default SymbolSelector;
