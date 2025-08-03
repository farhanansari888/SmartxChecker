import os
import requests

# RapidAPI key from environment
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# Truecaller API endpoint (RapidAPI)
BASE_URL = "https://truecaller4.p.rapidapi.com/api/v1/search"

# Function to get Truecaller data
def get_truecaller_data(phone_number: str):
    """
    Fetch caller details using Truecaller API via RapidAPI
    :param phone_number: e.g., +919876543210
    :return: dict with name, carrier, city, spam score OR None
    """
    try:
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "truecaller4.p.rapidapi.com"
        }
        params = {"phone": phone_number}

        response = requests.get(BASE_URL, headers=headers, params=params)
        data = response.json()

        # Debug print (optional)
        print("API Response:", data)

        # Parse response
        if "data" in data and len(data["data"]) > 0:
            info = data["data"][0]

            return {
                "name": info.get("name", "Unknown"),
                "carrier": info.get("carrier", "Unknown"),
                "city": info.get("city", "Unknown"),
                "score": info.get("score", "0")
            }
        else:
            return None

    except Exception as e:
        print("Error fetching Truecaller data:", e)
        return None
