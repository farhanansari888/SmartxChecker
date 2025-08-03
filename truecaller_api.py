import os
import requests
import logging

RAPIDAPI_KEY = os.getenv("X-RapidAPI-Key")  # Key from env

def get_truecaller_data(number: str):
    """
    Fetch data from Truecaller16 API using RapidAPI.
    """
    url = "https://truecaller16.p.rapidapi.com/api/v1/search"
    headers = {
        "x-rapidapi-host": "truecaller16.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    params = {
        "code": "91",   # Always 91 for India
        "number": number
    }

    logging.info(f"Making API request for {number} with params {params}")

    try:
        response = requests.get(url, headers=headers, params=params)
        logging.info(f"API Status Code: {response.status_code}")

        if response.status_code != 200:
            return f"❌ API request failed with status code {response.status_code}"

        data = response.json()
        logging.info(f"API Response JSON: {data}")

        # Handle no data
        if not data or "data" not in data or len(data["data"]) == 0:
            return f"❌ No data found for this number."

        user = data["data"][0]
        name = user.get("name", "N/A")
        carrier = user.get("carrier", "N/A")
        city = user.get("city", "N/A")
        email = user.get("email", "N/A")

        result = f"📞 Name: {name}\n📱 Carrier: {carrier}\n🏙 City: {city}\n✉ Email: {email}"
        return result

    except Exception as e:
        logging.error(f"Error in API call: {e}")
        return f"❌ Error: {str(e)}"
