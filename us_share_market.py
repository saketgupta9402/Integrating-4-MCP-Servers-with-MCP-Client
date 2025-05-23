from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import yfinance as yf
load_dotenv()

app = Flask(__name__)

MARKETSTACK_API_KEY = os.getenv("MARKETSTACK_API_KEY")

@app.route("/us_trading", methods=["GET"])
def get_trading_data():
    symbol = request.args.get("symbol")

    if not symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    url = f"http://api.marketstack.com/v1/eod/latest?access_key={MARKETSTACK_API_KEY}&symbols={symbol.upper()}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch trading data"}), response.status_code

        data = response.json()
        if "data" not in data or not data["data"]:
            return jsonify({"error": f"No data found for {symbol.upper()}."}), 404

        stock_data = data["data"][0]
        
        symbol_name = stock_data.get("symbol", symbol.upper())
        date = stock_data.get("date", "N/A")[:10]
        price = stock_data.get("close", "N/A")
        open_price = stock_data.get("open", "N/A")
        high = stock_data.get("high", "N/A")
        low = stock_data.get("low", "N/A")

        message = (
            f"\n📈 Trading data for {symbol_name} as of {date}:\n"
            f"🔹 Open: ${open_price}\n"
            f"🔹 Close: ${price}\n"
            f"🔹 High: ${high}\n"
            f"🔹 Low: ${low}"
        )

        return jsonify({"message": message})

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
