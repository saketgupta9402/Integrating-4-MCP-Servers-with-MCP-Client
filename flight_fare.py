from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

# Token cache
access_token = None

def get_amadeus_access_token():
    global access_token
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    access_token = response.json()["access_token"]
    return access_token

@app.route("/flight_fares", methods=["GET"])
def get_flight_fares():
    origin = request.args.get("from")
    destination = request.args.get("to")
    date = request.args.get("date")

    if not origin or not destination or not date:
        return jsonify({"error": "Missing 'from', 'to', or 'date'"}), 400

    try:
        get_amadeus_access_token()

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": 1,
            "currencyCode": "INR",
            "max": 5
        }
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch flight fares",
                            "status_code": response.status_code,
                            "details": response.text}), 500

        data = response.json().get("data", [])
        if not data:
            return jsonify({"message": "No flights found"}), 404

        flights_info = []
        for offer in data:
            itinerary = offer["itineraries"][0]["segments"][0]
            price = offer["price"]["total"]
            carrier_code = itinerary["carrierCode"]
            airline_name={
                "AI": "Air India",
                "G8": "GoAir",
                "SG": "SpiceJet",
                "UK": "AirAsia India",
                "6E": "IndiGo",
                "9W": "Jet Airways",
                "9V": "Vistara",
                "B6": "Air India Express",
                "G9": "TruJet",
                "QP": "Air Arabia",
                "QZ": "Air Arabia",
            }.get(carrier_code, carrier_code)
            departure = itinerary["departure"]["at"]
            arrival = itinerary["arrival"]["at"]

            flights_info.append({
                "airline": airline_name,
                "price": f"₹{price}",
                "departure_time": departure,
                "arrival_time": arrival
            })

        return jsonify({
            "message": f"Top flights from {origin} to {destination} on {date}",
            "flights": flights_info
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5005)
