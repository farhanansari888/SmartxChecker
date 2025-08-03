import requests
import os
import logging

# Setup logger
logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not RAPIDAPI_KEY:
    logger.error("❌ RAPIDAPI_KEY not set! Set environment variable first.")
else:
    logger.info("✅ RAPIDAPI_KEY loaded successfully.")

def lookup_number(phone_number, country_code="IN"):
    """
    Truecaller16 API se number lookup karega
    """
    url = "https://truecaller16.p.rapidapi.com/api/v1/search"
    querystring = {"number": phone_number, "countryCode": country_code}

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "truecaller16.p.rapidapi.com"
    }

    logger.info(f"Making API request for {phone_number} with country code {country_code}")

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        logger.info(f"API Status Code: {response.status_code}")
        data = response.json()
        logger.debug(f"Raw API Response: {data}")

        if response.status_code == 200 and data.get("data"):
            result = data["data"][0]
            name = result.get("name", "N/A")
            carrier = result.get("carrier", "Unknown")
            city = result.get("city", "Unknown")
            email = result.get("email", "Not available")

            return f"📞 *Name:* {name}\n🏙 *City:* {city}\n📡 *Carrier:* {carrier}\n✉️ *Email:* {email}"

        else:
            logger.warning(f"No data found for {phone_number}")
            return "❌ No data found for this number."

    except Exception as e:
        logger.error(f"API Error: {e}")
        return f"❌ API Error: {str(e)}"
