import React, { useState } from 'react';
import SymbolSelector from './components/SymbolSelector';
import ExpirySelector from './components/ExpirySelector';
import DataTable from './components/DataTable';

const App = () => {
  const [symbol, setSymbol] = useState('META');
  const [expiry, setExpiry] = useState('');

  return (
    <div>
      <h1>Options Streamer</h1>
      <SymbolSelector value={symbol} onChange={setSymbol} />
      {symbol && <ExpirySelector symbol={symbol} onChange={setExpiry} />}
      {symbol && expiry && <DataTable symbol={symbol} expiry={expiry} />}
    </div>
  );
};

export default App;
