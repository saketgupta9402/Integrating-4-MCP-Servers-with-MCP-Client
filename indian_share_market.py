from flask import Flask, request, jsonify
import requests
import yfinance as yf
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MARKETSTACK_API_KEY = os.getenv("MARKETSTACK_API_KEY")

@app.route("/indian_trading", methods=["GET"])
def get_trading_data():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    # Try MarketStack first
    try:
        marketstack_url = f"http://api.marketstack.com/v1/eod"
        params = {
            "access_key": MARKETSTACK_API_KEY,
            "symbols": symbol,
            "limit": 1
        }
        response = requests.get(marketstack_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                stock = data["data"][0]
                message = f"""📈 Trading data for {symbol} as of {stock['date'][:10]}:
🔹 Open: ₹{stock['open']}
🔹 Close: ₹{stock['close']}
🔹 High: ₹{stock['high']}
🔹 Low: ₹{stock['low']}"""
                return jsonify({"message": message})
    except Exception:
        pass  # Fail silently and try yfinance

    # Try yfinance fallback
    try:
        yf_symbol = symbol if '.' in symbol else f"{symbol}.NS"
        stock = yf.Ticker(yf_symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            return jsonify({"error": f"No data found for symbol: {symbol}"}), 404

        row = hist.iloc[-1]
        message = f"""📈 Trading data for {symbol}:
🔹 Open: ₹{row['Open']:.2f}
🔹 Close: ₹{row['Close']:.2f}
🔹 High: ₹{row['High']:.2f}
🔹 Low: ₹{row['Low']:.2f}"""
        return jsonify({"message": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5004)
