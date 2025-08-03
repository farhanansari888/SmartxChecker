import requests
import os

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

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

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get("data"):
            result = data["data"][0]
            name = result.get("name", "N/A")
            carrier = result.get("carrier", "Unknown")
            city = result.get("city", "Unknown")
            email = result.get("email", "Not available")

            return f"📞 *Name:* {name}\n🏙 *City:* {city}\n📡 *Carrier:* {carrier}\n✉️ *Email:* {email}"

        else:
            return "❌ No data found for this number."

    except Exception as e:
        return f"❌ API Error: {str(e)}"
