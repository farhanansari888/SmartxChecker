import os
import requests
import logging

# === Multiple API Keys (comma separated in ENV) ===
RAPIDAPI_KEYS = os.getenv("X-RapidAPI-Keys", "").split(",")
RAPIDAPI_KEYS = [k.strip() for k in RAPIDAPI_KEYS if k.strip()]  # clean list

# Key index tracker
current_key_index = 0

def get_next_key():
    """
    Rotate API keys sequentially.
    """
    global current_key_index
    if not RAPIDAPI_KEYS:
        return None
    key = RAPIDAPI_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(RAPIDAPI_KEYS)
    return key

def get_truecaller_data(number: str):
    """
    Fetch data from Truecaller16 API using rotating RapidAPI keys.
    """
    if not RAPIDAPI_KEYS:
        return "❌ No API keys configured.\n\n➤ Please contact admin: [𝐒𝐦𝐚𝐫𝐭𝐱𝐇𝐚𝐜𝐤𝐞𝐫](https://t.me/smartxhacker)"

    url = "https://truecaller16.p.rapidapi.com/api/v1/search"
    params = {
        "code": "91",
        "number": number
    }

    # Try all keys in rotation
    for _ in range(len(RAPIDAPI_KEYS)):
        key = get_next_key()
        headers = {
            "x-rapidapi-host": "truecaller16.p.rapidapi.com",
            "x-rapidapi-key": key
        }

        logging.info(f"Trying API key: {key[:6]}**** for number: {number}")

        try:
            response = requests.get(url, headers=headers, params=params)
            logging.info(f"API Status Code: {response.status_code}")

            # Handle specific error codes with reasons
            if response.status_code == 429:
                logging.warning("Rate limit exceeded for this key.")
                continue  # try next key

            if response.status_code == 403:
                logging.warning("Invalid/expired API key.")
                continue  # try next key

            if response.status_code == 500:
                return "❌ Server error from API. Please try again later."

            if response.status_code != 200:
                return "❌ Unknown API error occurred. Please contact admin."

            data = response.json()
            logging.info(f"API Response JSON: {data}")

            # Handle no data
            if not data or "data" not in data or len(data["data"]) == 0:
                return "❌ No data found for this number."

            user = data["data"][0]

            # Safe extraction (avoid list index errors)
            name = user.get("name", "N/A")
            dob = user.get("birthday", "N/A")

            phones = user.get("phones", [])
            addresses = user.get("addresses", [])
            emails = user.get("internetAddresses", [])

            carrier = phones[0].get("carrier", "N/A") if phones else "N/A"
            city = addresses[0].get("city", "N/A") if addresses else "N/A"
            email = emails[0].get("id", "N/A") if emails else "N/A"
            address = addresses[0].get("address", "N/A") if addresses else "N/A"

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
            continue  # try next key

    # If all keys fail
    return (
        "❌ All API keys exhausted or invalid.\n\n"
        "➤ Please contact admin: [𝐒𝐦𝐚𝐫𝐭𝐱𝐇𝐚𝐜𝐤𝐞𝐫](https://t.me/smartxhacker)"
    )
