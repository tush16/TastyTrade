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
      console.log("🔵 Incoming WS Data:", data);

      if (data.tt_type === "underlying_quote") {
        console.log("✅ Underlying Quote received:", data);
        setUnderlyingQuote(data);
      } else if (data.tt_type === "grouped_option_data") {
        const wsExpiry = data.expiry_date || data.expiry;
        const normalizedWsExpiry = wsExpiry?.slice(0, 10);
        const normalizedPropExpiry = expiry?.slice(0, 10);

        if (normalizedWsExpiry === normalizedPropExpiry) {
          console.log("✅ Option Data accepted:", data);
          setOptionData((prev) => {
            const filtered = prev.filter((item) => item.symbol !== data.symbol);
            return [...filtered, data];
          });
        } else {
          console.log(
            "⚠️ Skipped due to expiry mismatch:",
            "wsExpiry=", normalizedWsExpiry,
            "propExpiry=", normalizedPropExpiry
          );
        }
      } else {
        console.log("⚠️ Ignored WS Message:", data.tt_type);
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

  const groupedByStrike = optionData.reduce((acc, opt) => {
    console.log("➡️ Grouping strike:", opt.strike, "type:", opt.call_put);
    const strike = Number(opt.strike);
    if (!acc[strike]) {
      acc[strike] = { call: null, put: null };
    }
    if (opt.call_put === "C") {
      acc[strike].call = opt;
    } else if (opt.call_put === "P") {
      acc[strike].put = opt;
    }
    return acc;
  }, {});

  const formatNumber = (value, decimals = 2, suffix = "") => {
    if (value == null || isNaN(value)) return "-";
    return Number(value).toFixed(decimals) + suffix;
  };

  return (
    <div style={{
      padding: "1.5rem",
      fontFamily: "'Inter', 'Helvetica', 'Arial', sans-serif",
      maxWidth: "100%",
      margin: "0 auto",
      backgroundColor: "#ffffff",
      borderRadius: "12px",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
    }}>
      <style>
        {`
          .option-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            color: #333;
          }
          .option-table th, .option-table td {
            padding: 12px 8px;
            text-align: center;
            border-bottom: 1px solid #e5e7eb;
          }
          .option-table th {
            background: linear-gradient(to bottom, #f3f4f6, #e5e7eb);
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
            color: #1f2937;
            text-transform: uppercase;
            font-size: 12px;
          }
          .option-table tbody tr:nth-child(even) {
            background-color: #f9fafb;
          }
          .option-table tbody tr:hover {
            background-color: #f1f5f9;
            transition: background-color 0.2s;
          }
          .option-table .strike-cell {
            background-color: #e5e7eb;
            font-weight: 700;
            color: #1f2937;
          }
          .option-table .call-cell {
            background-color: rgba(187, 247, 208, 0.2);
          }
          .option-table .put-cell {
            background-color: rgba(254, 226, 226, 0.2);
          }
          .underlying-quote {
            background: linear-gradient(to right, #f3f4f6, #ffffff);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            font-size: 16px;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
          }
          .no-data {
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-style: italic;
          }
          @media (max-width: 768px) {
            .option-table {
              font-size: 12px;
            }
            .option-table th, .option-table td {
              padding: 8px 4px;
            }
            .underlying-quote {
              font-size: 14px;
              flex-direction: column;
              gap: 8px;
            }
          }
        `}
      </style>

      {underlyingQuote && (
        <div className="underlying-quote">
          <span>Underlying Quote: {symbol}</span>
          <div>
            <span style={{ color: "#15803d", marginRight: "1rem" }}>
              Bid: {formatNumber(underlyingQuote.bid_price)} ({underlyingQuote.bid_size})
            </span>
            <span style={{ color: "#b91c1c" }}>
              Ask: {formatNumber(underlyingQuote.ask_price)} ({underlyingQuote.ask_size})
            </span>
          </div>
        </div>
      )}

      <div style={{ overflowX: "auto", borderRadius: "8px" }}>
        <table className="option-table">
          <thead>
            <tr>
              <th colSpan={12} style={{ borderBottom: "2px solid #d1d5db" }}>CALLS</th>
              <th style={{ borderBottom: "2px solid #d1d5db" }}>Strike</th>
              <th colSpan={12} style={{ borderBottom: "2px solid #d1d5db" }}>PUTS</th>
            </tr>
            <tr>
              {[
                "Bid", "Ask", "Delta", "Theta", "Vega", "IV", "Mid", "PMP", "POP", "Max Profit", "Max Loss", "EV",
                "Strike",
                "Bid", "Ask", "Delta", "Theta", "Vega", "IV", "Mid", "PMP", "POP", "Max Profit", "Max Loss", "EV"
              ].map((header, idx) => (
                <th key={`${header}-${idx}`}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.keys(groupedByStrike).length === 0 ? (
              <tr>
                <td colSpan={25} className="no-data">
                  No option data available. Waiting for WebSocket data...
                </td>
              </tr>
            ) : (
              Object.keys(groupedByStrike)
                .map(Number)
                .sort((a, b) => a - b)
                .map((strike) => {
                  const { call, put } = groupedByStrike[strike] || {};
                  return (
                    <tr key={strike}>
                      {/* CALL side */}
                      <td className="call-cell">{formatNumber(call?.quote?.bid_price)}</td>
                      <td className="call-cell">{formatNumber(call?.quote?.ask_price)}</td>
                      <td className="call-cell">{formatNumber(call?.greeks?.delta, 4)}</td>
                      <td className="call-cell">{formatNumber(call?.greeks?.theta, 4)}</td>
                      <td className="call-cell">{formatNumber(call?.greeks?.vega, 4)}</td>
                      <td className="call-cell">{call?.greeks?.IV ? formatNumber(call.greeks.IV * 100, 2, "%") : "-"}</td>
                      <td className="call-cell">{formatNumber(call?.calculations?.mid_price)}</td>
                      <td className="call-cell">{formatNumber(call?.calculations?.pmp, 2, "%")}</td>
                      <td className="call-cell">{formatNumber(call?.calculations?.pop, 2, "%")}</td>
                      <td className="call-cell">{formatNumber(call?.calculations?.max_profit)}</td>
                      <td className="call-cell">{call?.calculations?.max_loss ?? "-"}</td>
                      <td className="call-cell">{formatNumber(call?.calculations?.ev)}</td>

                      {/* STRIKE */}
                      <td className="strike-cell">{formatNumber(strike, 0)}</td>

                      {/* PUT side */}
                      <td className="put-cell">{formatNumber(put?.quote?.bid_price)}</td>
                      <td className="put-cell">{formatNumber(put?.quote?.ask_price)}</td>
                      <td className="put-cell">{formatNumber(put?.greeks?.delta, 4)}</td>
                      <td className="put-cell">{formatNumber(put?.greeks?.theta, 4)}</td>
                      <td className="put-cell">{formatNumber(put?.greeks?.vega, 4)}</td>
                      <td className="put-cell">{put?.greeks?.IV ? formatNumber(put.greeks.IV * 100, 2, "%") : "-"}</td>
                      <td className="put-cell">{formatNumber(put?.calculations?.mid_price)}</td>
                      <td className="put-cell">{formatNumber(put?.calculations?.pmp, 2, "%")}</td>
                      <td className="put-cell">{formatNumber(put?.calculations?.pop, 2, "%")}</td>
                      <td className="put-cell">{formatNumber(put?.calculations?.max_profit)}</td>
                      <td className="put-cell">{put?.calculations?.max_loss ?? "-"}</td>
                      <td className="put-cell">{formatNumber(put?.calculations?.ev)}</td>
                    </tr>
                  );
                })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;