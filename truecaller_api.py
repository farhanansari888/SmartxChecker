import os
import requests
import logging

# === Config ===
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

API_URL = "https://truecaller16.p.rapidapi.com/api/v1/getDetails"

HEADERS = {
    "x-rapidapi-host": "truecaller16.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY
}

# === Logger Setup ===
logger = logging.getLogger(__name__)

def get_number_details(number: str, country_code: str = "IN"):
    """
    RapidAPI Truecaller16 API se number details fetch karta hai
    """

    # +91 ke bina 91 rakho
    if number.startswith("+"):
        number = number.replace("+", "")
    if not number.startswith("91"):
        number = "91" + number

    params = {
        "phone": number,
        "countryCode": country_code,
        "installationId": "eb633e0a-443d-44f5-bb4c-aaa9dfe5fc0d"  # required by API
    }

    try:
        logger.info(f"Making API request for {number} with country code {country_code}")

        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=10)
        logger.info(f"API Status Code: {response.status_code}")

        if response.status_code != 200:
            return f"❌ API request failed with status code {response.status_code}"

        data = response.json()
        logger.debug(f"Full API response: {data}")

        # Agar 'data' key nahi hai
        if not data or "data" not in data or not data["data"]:
            logger.warning(f"No data found for {number}")
            return f"❌ No data found for this number."

        details = data["data"][0]
        name = details.get("name", "N/A")
        carrier = details.get("carrier", "N/A")
        city = details.get("city", "N/A")

        result = (
            f"📞 *Number Details:*\n\n"
            f"**Name:** {name}\n"
            f"**Carrier:** {carrier}\n"
            f"**City:** {city}\n"
        )

        logger.info(f"API Response for {number}: {result}")
        return result

    except Exception as e:
        logger.exception(f"Error fetching data for {number}")
        return f"❌ Error: {str(e)}"
