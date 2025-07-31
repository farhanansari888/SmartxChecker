import requests
import json
from fake_useragent import UserAgent

def brn6(ccx):
    """
    Stripe checker logic
    ccx format: "card|month|year|cvv"
    Returns: "Approved" / "declined" / "error"
    """
    try:
        ccx = ccx.strip()
        n, mm, yy, cvc = ccx.split("|")
        if "20" in yy:
            yy = yy.split("20")[1]

        user_agent = UserAgent().random

        # Stripe API headers
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': user_agent,
        }

        # First call - create payment method
        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}'
        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)

        if response.status_code != 200:
            return 'error'

        pm_id = response.json().get('id')
        if not pm_id:
            return 'declined'

        # Second call (mock) - simulate success/failure
        # In real stripe endpoints, use pm_id with setup_intent or payment_intent
        if "pm_" in pm_id:
            return "Approved"
        else:
            return "declined"

    except Exception as e:
        print("Error in brn6:", e)
        return "error"
