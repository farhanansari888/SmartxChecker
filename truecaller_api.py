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

        # Extract fields
        name = user.get("name", "N/A")
        dob = user.get("birthday", "N/A")
        carrier = user.get("phones", [{}])[0].get("carrier", "N/A")
        city = user.get("addresses", [{}])[0].get("city", "N/A")
        email = user.get("internetAddresses", [{}])[0].get("id", "N/A")
        address = user.get("addresses", [{}])[0].get("address", "N/A")

        # Fancy formatted response
        result = (
            "✨ 𝐒𝐦𝐚𝐫𝐭𝐱𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐑𝐞𝐬𝐮𝐥𝐭 ✨\n\n"
            f"• 𝐍𝐚𝐦𝐞: {name}\n"
            f"• 𝐃𝐎𝐁: {dob}\n"
            f"• 𝐂𝐚𝐫𝐫𝐢𝐞𝐫: {carrier}\n"
            f"• 𝐂𝐢𝐭𝐲: {city}\n"
            f"• 𝐄𝐦𝐚𝐢𝐥: {email}\n"
            f"• 𝐀𝐝𝐝𝐫𝐞𝐬𝐬: {address}\n\n"
            "──────────────\n"
            "➤ 𝐁𝐨𝐭 𝐁𝐲: [𝐒𝐦𝐚𝐫𝐭𝐱𝐇𝐚𝐜𝐤𝐞𝐫](https://t.me/smartxhacker)"
        )

        return result

    except Exception as e:
        logging.error(f"Error in API call: {e}")
        return f"❌ Error: {str(e)}"
