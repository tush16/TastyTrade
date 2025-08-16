import React, { useState, useEffect } from 'react';
import SelectorContainer from './containers/SelectorContainer';
import DataTable from './components/DataTable';

const App = () => {
  const [symbol, setSymbol] = useState('META');
  const [expiry, setExpiry] = useState('');
  const [optionSymbols, setOptionSymbols] = useState([]);

  useEffect(() => {
    setExpiry('');
    setOptionSymbols([]);
  }, [symbol]);

  return (
    <div style={{
      fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif",
      minHeight: '100vh',
      backgroundColor: '#f9fafb',
    }}>
      <style>
        {`
          .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
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
          .selector-container {
            margin-bottom: 2rem; /* Space between SelectorContainer and DataTable */
            padding-top: 4rem; /* Account for fixed navbar */
            max-width: 1200px;
            width: 30%;
            box-sizing: border-box;
          }
        `}
      </style>

      <nav className="navbar">
        <h1 className="navbar-title">Options Analytics</h1>
      </nav>

      <div className="content-container">
        <div className="selector-container">
          <SelectorContainer
            symbol={symbol}
            onSymbolChange={setSymbol}
            onExpiryChange={({ expiry: selectedExpiry, optionSymbols: symbols }) => {
              setExpiry(selectedExpiry);
              setOptionSymbols(symbols);
            }}
          />
        </div>
        {symbol && expiry && optionSymbols.length > 0 && (
          <DataTable symbol={symbol} expiry={expiry} optionSymbols={optionSymbols} />
        )}
      </div>
    </div>
  );
};

export default App;