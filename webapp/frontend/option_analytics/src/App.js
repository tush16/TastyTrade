import React, { useState, useEffect } from 'react';
import SymbolSelector from './components/SymbolSelector';
import ExpirySelector from './components/ExpirySelector';
import DataTable from './components/DataTable';

const App = () => {
  const [symbol, setSymbol] = useState('META');
  const [expiry, setExpiry] = useState('');
  const [optionSymbols, setOptionSymbols] = useState([]);

  // Reset expiry & option symbols when symbol changes
  useEffect(() => {
    setExpiry('');
    setOptionSymbols([]);
  }, [symbol]);

  return (
    <div style={{
      fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif",
      minHeight: '100vh',
      width: '100vw',          // take full screen width
      backgroundColor: '#f9fafb',
      paddingTop: '4rem',       // space for fixed navbar
      boxSizing: 'border-box',  // include padding in width
    }}>
      <style>
        {`
          .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            background: linear-gradient(to bottom, #f3f4f6, #ffffff);
            padding: 1rem 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          .navbar-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
          }
          .selectors-row {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: flex-start;
            margin-bottom: 1rem;
            padding: 0 1rem;
            width: 100%;
          }
          .content-container {
            width: 100%;
            padding: 0 1rem;
            box-sizing: border-box;
          }
        `}
      </style>

      <nav className="navbar">
        <h1 className="navbar-title">Option-Chain Analytics</h1>
      </nav>

      <div className="content-container">
        <div className="selectors-row">
          <SymbolSelector value={symbol} onChange={setSymbol} />
          <ExpirySelector
            symbol={symbol}
            selectedExpiry={expiry}
            onChange={({ expiry: selectedExpiry, optionSymbols: symbols }) => {
              setExpiry(selectedExpiry);
              setOptionSymbols(symbols);
            }}
          />
        </div>

        {symbol && expiry && optionSymbols.length > 0 && (
          <div style={{ width: '100%', overflowX: 'auto' }}>
            <DataTable symbol={symbol} expiry={expiry} optionSymbols={optionSymbols} />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
