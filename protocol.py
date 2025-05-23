from shared.protocol import QueryType

SERVER_ENDPOINTS = {
    QueryType.WEATHER: "http://localhost:5002/weather",
    QueryType.US_TRADING: "http://localhost:5003/us_trading",
    QueryType.INDIAN_TRADING: "http://localhost:5004/indian_trading",
    QueryType.FLIGHT_FARES: "http://localhost:5005/flight_fares"
}
