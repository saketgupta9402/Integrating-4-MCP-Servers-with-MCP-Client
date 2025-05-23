import requests
from client.protocol import SERVER_ENDPOINTS
from client.router import classify_query, extract_parameters
from shared.protocol import QueryType

# Main function to handle user interaction
def main():
    # Take user input
    user_query = input("💬 Ask me anything regarding weather, US stock market, Indian stock market, or flight fares: ")

    # Classify the query using the LLM
    query_type = classify_query(user_query)
    print(f"[Router] 🧠 LLM classified as: {query_type.value}")

    # Extract necessary parameters from the query using LLM
    params = extract_parameters(user_query, query_type)
    print(f"[Router] 📦 Extracted params: {params}")

    # Stop if parameter extraction failed
    if "error" in params:
        print("⚠️ Could not extract necessary parameters from your query.")
        return

    # Normalize values to correct format
    if query_type in {QueryType.US_TRADING, QueryType.INDIAN_TRADING}:
        if "symbol" in params:
            params["symbol"] = params["symbol"].upper()
    elif query_type == QueryType.WEATHER:
        if "city" in params:
            params["city"] = params["city"].title()
    elif query_type == QueryType.FLIGHT_FARES:
        for k in ("from", "to"):
            if k in params:
                params[k] = params[k].upper()

    # Send request to the appropriate server
    url = SERVER_ENDPOINTS[query_type]
    response = requests.get(url, params=params)

    # Handle and format the server response
    print("\n🔎 Server Response:\n")
    try:
        data = response.json()
        if isinstance(data, dict):
            if "message" in data:
                print(data["message"])
            if query_type == QueryType.FLIGHT_FARES and "flights" in data:
                print("\nTop Flight Options:\n")
                for i, flight in enumerate(data["flights"], start=1):
                    print(f"""Flight {i}
                        ✈️  Airline        : {flight.get('airline', 'Unknown')}
                        🕒 Departure Time : {flight.get('departure_time', 'N/A')}
                        🛬 Arrival Time   : {flight.get('arrival_time', 'N/A')}
                        💰 Price          : {flight.get('price', 'N/A')}
                        {"-" * 40}""")
        else:
            print(data)
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        print("Raw response:", response.text)

if __name__ == "__main__":
    main()
