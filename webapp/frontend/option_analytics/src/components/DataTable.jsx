import React, { useEffect, useState, useRef } from "react";

const DataTable = ({ symbol, expiry }) => {
  const [optionData, setOptionData] = useState([]);
  const [underlyingQuote, setUnderlyingQuote] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket(
      `ws://localhost:8000/ws/chain?symbol=${symbol}&expiry=${expiry}`
    );

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.tt_type === "underlying_quote") {
        setUnderlyingQuote(data);
      } else if (data.tt_type === "grouped_option_data" && data.expiry === expiry) {
        setOptionData((prev) => {
          // Replace if already exists
          const updated = prev.filter((item) => item.symbol !== data.symbol);
          return [...updated, data];
        });
      }
    };

    return () => {
      ws.current?.close();
      setOptionData([]); // clear table when expiry changes
    };
  }, [symbol, expiry]);

  return (
    <div>
      {underlyingQuote && (
        <div style={{ marginBottom: "1rem", fontWeight: "bold" }}>
          Underlying Quote — Bid: {underlyingQuote.bid_price} ({underlyingQuote.bid_size}) | 
          Ask: {underlyingQuote.ask_price} ({underlyingQuote.ask_size})
        </div>
      )}
      <table border="1" cellPadding="4">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Strike</th>
            <th>Type</th>
            <th>Expiry</th>
            <th>Bid</th>
            <th>Ask</th>
            <th>Delta</th>
            <th>Gamma</th>
            <th>Theta</th>
            <th>Vega</th>
            <th>IV</th>
          </tr>
        </thead>
        <tbody>
          {optionData.map((opt) => (
            <tr key={opt.symbol}>
              <td>{opt.symbol}</td>
              <td>{opt.strike}</td>
              <td>{opt.type}</td>
              <td>{opt.expiry}</td>
              <td>{opt.quote.bid_price}</td>
              <td>{opt.quote.ask_price}</td>
              <td>{opt.greeks.delta.toFixed(4)}</td>
              <td>{opt.greeks.gamma.toFixed(4)}</td>
              <td>{opt.greeks.theta.toFixed(4)}</td>
              <td>{opt.greeks.vega.toFixed(4)}</td>
              <td>{(opt.greeks.IV * 100).toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
