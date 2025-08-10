import React, { useState, useEffect } from 'react';
import SymbolSelector from './components/SymbolSelector';
import ExpirySelector from './components/ExpirySelector';
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
    <div>
      <h1>Options Analytics</h1>
      <SymbolSelector value={symbol} onChange={setSymbol} />
      {symbol && (
        <ExpirySelector
          symbol={symbol}
          onChange={({ expiry: selectedExpiry, optionSymbols: symbols }) => {
            setExpiry(selectedExpiry);
            setOptionSymbols(symbols);
          }}
        />
      )}
      {symbol && expiry && optionSymbols.length > 0 && (
        <DataTable symbol={symbol} expiry={expiry} optionSymbols={optionSymbols} />
      )}
    </div>
  );
};

export default App;