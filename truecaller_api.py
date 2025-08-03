import os
import requests

# RapidAPI credentials
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")  # Render par env me dalna
RAPIDAPI_HOST = "callapp.p.rapidapi.com"

API_URL = "https://callapp.p.rapidapi.com/api/"

def search_number(phone_number: str):
    """
    CallApp API se phone number search karke data return karega
    """
    try:
        url = f"{API_URL}v1/lookup"
        querystring = {"number": phone_number}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        # Agar data mila to return karo, warna None
        if data and "name" in data:
            return data
        else:
            return None

    except Exception as e:
        print(f"Error in search_number: {e}")
        return None
