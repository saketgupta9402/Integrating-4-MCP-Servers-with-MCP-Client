from enum import Enum

class QueryType(str, Enum):
    WEATHER = "weather"
    US_TRADING = "us_trading"
    INDIAN_TRADING = "indian_trading"
    FLIGHT_FARES = "flight_fares"
