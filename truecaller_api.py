import os
import requests
import logging

# RapidAPI Key (Truecaller16 API)
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
API_URL = "https://truecaller16.p.rapidapi.com/api/v1/search"

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "truecaller16.p.rapidapi.com"
}

def search_number(phone_number: str, country_code: str = "IN") -> dict:
    """
    Lookup phone number using Truecaller16 API
    """
    try:
        logging.info(f"Making API request for {phone_number} with country code {country_code}")

        params = {
            "phone": phone_number,
            "countryCode": country_code
        }

        response = requests.get(API_URL, headers=HEADERS, params=params)
        logging.info(f"API Status Code: {response.status_code}")

        if response.status_code != 200:
            return {"error": f"API error: {response.status_code}"}

        data = response.json()

        # Full raw response debug
        logging.debug(f"API Raw Response: {data}")

        # Check agar data hai
        if not data or "data" not in data or not data["data"]:
            logging.warning(f"No data found for {phone_number}")
            return {"error": "No data found for this number."}

        result = data["data"][0]
        return {
            "name": result.get("name", "Unknown"),
            "carrier": result.get("carrier", "Unknown"),
            "country": result.get("countryCode", "Unknown"),
            "score": result.get("score", "N/A"),
            "spam": result.get("spam", False)
        }

    except Exception as e:
        logging.error(f"Exception in search_number: {e}")
        return {"error": str(e)}
