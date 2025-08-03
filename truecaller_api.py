import os
import requests
import logging

# RapidAPI Key
API_KEY = os.getenv("X-RapidAPI-Key")

# Base URL for Truecaller16 API
BASE_URL = "https://truecaller16.p.rapidapi.com/api/v1/search"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "truecaller16.p.rapidapi.com"
}

def search_number(phone: str) -> dict:
    """
    Search phone number details using Truecaller16 API.
    phone: 10-digit number (without +91)
    """

    # Query parameters
    params = {
        "number": phone,
        "code": "91"  # For India
    }

    try:
        logging.info(f"Making API request for {phone} with country code 91")
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        logging.info(f"API Status Code: {response.status_code}")

        if response.status_code != 200:
            return {"error": f"API error: {response.status_code}"}

        data = response.json()
        logging.info(f"Raw API Response: {data}")

        # Handle no data scenario
        if not data or "data" not in data or len(data["data"]) == 0:
            logging.warning(f"No data found for {phone}")
            return {"error": "No data found for this number."}

        # Extract first record
        record = data["data"][0]

        return {
            "name": record.get("name", "Unknown"),
            "carrier": record.get("carrier", "Unknown"),
            "country": record.get("countryDetails", {}).get("name", "Unknown"),
            "score": record.get("score", 0),
            "spam": record.get("spam", False)
        }

    except Exception as e:
        logging.error(f"Exception during API request: {e}")
        return {"error": str(e)}
