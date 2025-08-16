import React, { useEffect, useState, useRef } from "react";

const DataTable = ({ symbol, expiry, optionSymbols }) => {
  const [optionData, setOptionData] = useState([]);
  const [underlyingQuote, setUnderlyingQuote] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    if (!symbol || !expiry || !optionSymbols || optionSymbols.length === 0) {
      setOptionData([]);
      setUnderlyingQuote(null);
      return;
    }

    const optionSymbolsParam = optionSymbols.map(sym => encodeURIComponent(sym)).join(",");
    const wsUrl = `ws://localhost:8000/ws/chain?symbol=${encodeURIComponent(symbol)}&expiry=${encodeURIComponent(expiry)}&option_symbols=${optionSymbolsParam}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.tt_type === "underlying_quote") {
        setUnderlyingQuote(data);
      } else if (data.tt_type === "grouped_option_data" && data.expiry === expiry) {
        setOptionData((prev) => {
          const filtered = prev.filter((item) => item.symbol !== data.symbol);
          return [...filtered, data];
        });
      }
    };

    ws.current.onerror = (error) => {
      console.error("WebSocket error", error);
    };

    return () => {
      ws.current?.close();
      setOptionData([]);
      setUnderlyingQuote(null);
    };
  }, [symbol, expiry, optionSymbols]);

  // Group by strike price
  const groupedByStrike = optionData.reduce((acc, opt) => {
    if (!acc[opt.strike]) {
      acc[opt.strike] = { call: null, put: null };
    }
    if (opt.type.toLowerCase() === "call") {
      acc[opt.strike].call = opt;
    } else if (opt.type.toLowerCase() === "put") {
      acc[opt.strike].put = opt;
    }
    return acc;
  }, {});

  return (
    <div style={{ padding: "1rem", fontFamily: "Arial, sans-serif" }}>
      {underlyingQuote && (
        <div style={{ marginBottom: "1rem", fontWeight: "bold", fontSize: "1.1rem", backgroundColor: "#f0f4f8", padding: "8px 12px", borderRadius: "6px" }}>
          Underlying Quote —{" "}
          <span style={{ color: "green" }}>Bid: {underlyingQuote.bid_price} ({underlyingQuote.bid_size})</span>{" "}
          |{" "}
          <span style={{ color: "red" }}>Ask: {underlyingQuote.ask_price} ({underlyingQuote.ask_size})</span>
        </div>
      )}

      <div style={{ overflowX: "auto", border: "1px solid #ddd", borderRadius: "8px" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "900px" }}>
            <thead style={{ backgroundColor: "#f9fafb" }}>
              <tr>
                <th colSpan={6} style={{ textAlign: "center", borderBottom: "2px solid #ddd" }}>CALLS</th>
                <th style={{ textAlign: "center", borderBottom: "2px solid #ddd" }}>Strike</th>
                <th colSpan={6} style={{ textAlign: "center", borderBottom: "2px solid #ddd" }}>PUTS</th>
              </tr>
              <tr>
                {["Bid", "Ask", "Delta", "Theta", "Vega", "IV", "Strike", "Bid", "Ask", "Delta", "Theta", "Vega", "IV"].map((header) => (
                  <th
                    key={header}
                    style={{
                      padding: "10px",
                      textAlign: "center",
                      fontWeight: "600",
                      fontSize: "0.85rem",
                      borderBottom: "2px solid #ddd",
                      color: "#555",
                    }}
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
          <tbody>
            {Object.keys(groupedByStrike).sort((a, b) => a - b).map((strike) => {
              const { call, put } = groupedByStrike[strike] || {};
              return (
                <tr key={strike}>
                  {/* CALL side */}
                  <td style={{ padding: "8px", textAlign: "center" }}>{call?.quote.bid_price ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{call?.quote.ask_price ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{call?.greeks.delta?.toFixed(4) ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{call?.greeks.theta?.toFixed(4) ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{call?.greeks.vega?.toFixed(4) ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{call ? (call.greeks.IV * 100).toFixed(2) + "%" : "-"}</td>

                  {/* STRIKE in middle */}
                  <td style={{ padding: "8px", fontWeight: "bold", textAlign: "center" }}>{strike}</td>

                  {/* PUT side */}
                  <td style={{ padding: "8px", textAlign: "center" }}>{put?.quote.bid_price ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{put?.quote.ask_price ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{put?.greeks.delta?.toFixed(4) ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{put?.greeks.theta?.toFixed(4) ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{put?.greeks.vega?.toFixed(4) ?? "-"}</td>
                  <td style={{ padding: "8px", textAlign: "center" }}>{put ? (put.greeks.IV * 100).toFixed(2) + "%" : "-"}</td>
                </tr>
              );
            })}
            {Object.keys(groupedByStrike).length === 0 && (
              <tr>
                <td colSpan={11} style={{ padding: "12px", textAlign: "center" }}>
                  No option data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;
