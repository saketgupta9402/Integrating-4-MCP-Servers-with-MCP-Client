import os
from groq import Groq
from dotenv import load_dotenv
from shared.protocol import QueryType
import json
import re

# Load environment variables
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define category mapping
CATEGORY_MAPPING = {
    "weather": QueryType.WEATHER,
    "climate": QueryType.WEATHER,
    "forecast": QueryType.WEATHER,
    "us stock": QueryType.US_TRADING,
    "us_trading": QueryType.US_TRADING,
    "us trading": QueryType.US_TRADING,
    "stock price usa": QueryType.US_TRADING,
    "indian stock": QueryType.INDIAN_TRADING,
    "indian_trading": QueryType.INDIAN_TRADING,
    "nse": QueryType.INDIAN_TRADING,
    "bse": QueryType.INDIAN_TRADING,
    "flight": QueryType.FLIGHT_FARES,
    "flights": QueryType.FLIGHT_FARES,
    "flight_fares": QueryType.FLIGHT_FARES,
    "airfare": QueryType.FLIGHT_FARES
}

# Use LLM to classify the query into one of the categories      
def classify_query(user_input: str) -> QueryType:
    prompt = f"""
You are a smart assistant that classifies queries into one of these categories:
- weather
- us_trading
- indian_trading
- flight_fares

Classify this query into one of the above categories only.

Query: "{user_input}"

Respond with only the category word.
"""

    try:
        #  Send the prompt to the LLM and get the classification response
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw_category = response.choices[0].message.content.strip().lower()
        print(f"[Router] LLM classified query as: {raw_category}")
        
        # Normalize and validate the classification response
        if raw_category in CATEGORY_MAPPING:
            return CATEGORY_MAPPING[raw_category]
        if raw_category in QueryType._value2member_map_:
            return QueryType(raw_category)
        raise ValueError(f"Unrecognized classification: {raw_category}")

    except Exception as e:
        print(f"[Router Error] Failed to classify query: {e}")
        print("[Router] Defaulting to manual selection.")
        return fallback_manual_query_type()


# Fallback to manual selection if the LLM fails to classify the query
def fallback_manual_query_type() -> QueryType:
    print("\nPlease choose your query type manually:")
    for qt in QueryType:
        print(f"- {qt.value}")
    while True:
        user_choice = input("Enter category: ").strip().lower()
        if user_choice in QueryType._value2member_map_:
            return QueryType(user_choice)
        print("Invalid choice. Try again.")


# Use LLM to extract the parameters from the user query
def extract_parameters(user_input: str, query_type: QueryType) -> dict:
    base_prompt = f"""
You are a helpful assistant. Extract the required parameters from the user query as a flat JSON object.

Use valid JSON syntax only. Use the following keys:
- weather: {{ "city": "City Name" }}
- us_trading: {{ "symbol": "StockSymbol" }}
- indian_trading: {{ "symbol": "StockSymbol" }}
- flight_fares: {{ "from": "IATA", "to": "IATA", "date": "YYYY-MM-DD" }}

Only return a valid JSON object. Do not include comments or additional explanation.

Query: "{user_input}"
"""

    try:
        # Ask the LLM to extract the parameters from the user query
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": base_prompt}],
            temperature=0.1
        )
        raw_json = response.choices[0].message.content.strip()
        print(f"[Router] Raw JSON: {raw_json}")

        # Optional cleanup to isolate valid JSON block
        match = re.search(r"\{.*\}", raw_json, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON found")
        raw_json = match.group(0)

        # Replace special characters with standard quotes
        raw_json = raw_json.replace('“', '"').replace('”', '"').replace("'", '"')

        # Parse the JSON object
        parsed = json.loads(raw_json)

        if isinstance(parsed, dict) and query_type.value in parsed:
            parsed = parsed[query_type.value]

        # Extract the parameters for the specific query type
        if query_type == QueryType.WEATHER and isinstance(parsed, dict) and "weather" in parsed:
            return {"city": parsed["weather"]}
        if query_type in {QueryType.US_TRADING, QueryType.INDIAN_TRADING} and "symbol" in parsed:
            return {"symbol": parsed["symbol"]}
        if query_type == QueryType.FLIGHT_FARES and all(k in parsed for k in ["from", "to", "date"]):
            return parsed

        # Return the parsed parameters
        return parsed
    
    except Exception as e:
        print(f"[Router Error] Parameter extraction failed: {e}")
        return {"error": "parameter extraction failed"}
