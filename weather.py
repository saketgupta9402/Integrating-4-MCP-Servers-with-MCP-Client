from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("WEATHERSTACK_API_KEY")

@app.route("/weather")
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City is required"}), 400

    url = f"http://api.weatherstack.com/current?access_key={API_KEY}&query={city}"
    res = requests.get(url)
    data = res.json()

    try:
        current = data["current"]
        location = data["location"]

        response = {
            "message": (
                f"\n📍 Weather update for {location['name']}, {location['region']} ({location['country']}):"
                f"\n🌤️ {current['weather_descriptions'][0]} with a temperature of {current['temperature']}°C."
                f"\n💧 Humidity: {current['humidity']}%, 🌬️ Wind: {current['wind_speed']} km/h from {current['wind_dir']}."
                f"\n🌅 Sunrise: {current.get('astro', {}).get('sunrise', 'N/A')}, 🌇 Sunset: {current.get('astro', {}).get('sunset', 'N/A')}."
                f"\n📍 Local time: {location['localtime']}."
            )
        }
        return jsonify(response)

    except KeyError:
        return jsonify({"error": "Could not retrieve weather details."}), 500

if __name__ == "__main__":
    app.run(port=5002)
