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

    // Build the comma-separated list for query param, encodeURIComponent to be safe
    const optionSymbolsParam = optionSymbols.map(sym => encodeURIComponent(sym)).join(",");

    const wsUrl = `ws://localhost:8000/ws/chain?symbol=${encodeURIComponent(symbol)}&expiry=${encodeURIComponent(expiry)}&option_symbols=${optionSymbolsParam}`;
    console.log("Connecting to WebSocket:", wsUrl);
    ws.current = new WebSocket(wsUrl);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.tt_type === "underlying_quote") {
        setUnderlyingQuote(data);
      } else if (
        data.tt_type === "grouped_option_data" &&
        data.expiry === expiry
      ) {
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

  return (
    <div style={{ padding: "1rem", fontFamily: "Arial, sans-serif" }}>
      {underlyingQuote && (
        <div
          style={{
            marginBottom: "1rem",
            fontWeight: "bold",
            fontSize: "1.1rem",
            color: "#333",
            backgroundColor: "#f0f4f8",
            padding: "8px 12px",
            borderRadius: "6px",
          }}
        >
          Underlying Quote —{" "}
          <span style={{ color: "green" }}>
            Bid: {underlyingQuote.bid_price} ({underlyingQuote.bid_size})
          </span>{" "}
          |{" "}
          <span style={{ color: "red" }}>
            Ask: {underlyingQuote.ask_price} ({underlyingQuote.ask_size})
          </span>
        </div>
      )}
      <div
        style={{
          overflowX: "auto",
          border: "1px solid #ddd",
          borderRadius: "8px",
          boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            minWidth: "700px",
          }}
        >
          <thead style={{ backgroundColor: "#f9fafb" }}>
            <tr>
              {[
                "Symbol",
                "Strike",
                "Type",
                "Expiry",
                "Bid",
                "Ask",
                "Delta",
                "Gamma",
                "Theta",
                "Vega",
                "IV",
              ].map((header) => (
                <th
                  key={header}
                  style={{
                    padding: "10px",
                    textAlign: "left",
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
            {optionData.map((opt) => (
              <tr
                key={opt.symbol}
                style={{
                  borderBottom: "1px solid #eee",
                  transition: "background-color 0.2s ease",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#f0f4f8")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = "transparent")
                }
              >
                <td style={{ padding: "8px" }}>{opt.symbol}</td>
                <td style={{ padding: "8px" }}>{opt.strike}</td>
                <td style={{ padding: "8px" }}>{opt.type}</td>
                <td style={{ padding: "8px" }}>{opt.expiry}</td>
                <td style={{ padding: "8px" }}>{opt.quote.bid_price}</td>
                <td style={{ padding: "8px" }}>{opt.quote.ask_price}</td>
                <td style={{ padding: "8px" }}>{opt.greeks.delta.toFixed(4)}</td>
                <td style={{ padding: "8px" }}>{opt.greeks.gamma.toFixed(4)}</td>
                <td style={{ padding: "8px" }}>{opt.greeks.theta.toFixed(4)}</td>
                <td style={{ padding: "8px" }}>{opt.greeks.vega.toFixed(4)}</td>
                <td style={{ padding: "8px" }}>
                  {(opt.greeks.IV * 100).toFixed(2)}%
                </td>
              </tr>
            ))}
            {optionData.length === 0 && (
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
