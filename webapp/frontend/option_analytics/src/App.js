import React, { useState, useEffect } from 'react';
import SymbolSelector from './components/SymbolSelector';
import ExpirySelector from './components/ExpirySelector';
import DataTable from './components/DataTable';

const App = () => {
  const [symbol, setSymbol] = useState('');
  const [expiry, setExpiry] = useState('');
  const [optionSymbols, setOptionSymbols] = useState([]);

  useEffect(() => {
    setExpiry('');
    setOptionSymbols([]);
  }, [symbol]);

  const showPlaceholder = !symbol || !expiry || optionSymbols.length === 0;

  return (
    <div style={{
      fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif",
      minHeight: '100vh',
      width: '100vw',
      backgroundColor: '#f9fafb',
      paddingTop: '4rem',
      boxSizing: 'border-box',
    }}>
      <style>
        {`
          .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            background: #000000;
            padding: 1rem 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          .navbar-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
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
        <img src="/candlestick-chart.png" alt="Logo" width="32" height="32" style={{ marginRight: '10px' }} />
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

        {showPlaceholder ? (
          <div style={{
            marginTop: '2rem',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '60vh',
          }}>
            <img 
              src="/bar-chart.png" 
              alt="Select symbol and expiry"
              style={{ width: '200px', marginBottom: '16px' }}
            />
            <div style={{
              fontSize: '18px',
              color: '#6b7280',
              textAlign: 'center'
            }}>
              Please select a symbol and expiry to visualize the option chain
            </div>
          </div>
        ) : (
          <div style={{ width: '100%', overflowX: 'auto' }}>
            <DataTable symbol={symbol} expiry={expiry} optionSymbols={optionSymbols} />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
