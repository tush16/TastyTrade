import numpy as np

if not hasattr(np, "recfromcsv"):
    np.recfromcsv = np.genfromtxt

import yfinance as yf
from pypnf import PointFigureChart


class PNFService:
    @staticmethod
    def fetch_timeseries(
        symbol: str, start: str = "2023-01-01", end: str = "2025-01-01"
    ):
        data = yf.Ticker(symbol).history(start=start, end=end)

        if data.empty:
            raise ValueError(f"No data found for {symbol}")

        data.reset_index(level=0, inplace=True)
        data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")
        ts = data[["Date", "Open", "High", "Low", "Close"]]
        return ts.to_dict("list")

    @staticmethod
    def generate_pnf_chart(ts: dict, symbol: str, boxsize: int = 2, reversal: int = 3):
        pnf = PointFigureChart(
            ts=ts,
            method="h/l",  # high/low is usually used for the fancy chart
            reversal=reversal,
            boxsize=boxsize,
            scaling="abs",
            title=symbol,
        )

        # add indicators (fancy chart)
        pnf.bollinger(5, 2)
        pnf.donchian(8, 2)
        pnf.psar(0.02, 0.2)

        # render chart
        pnf.show()
