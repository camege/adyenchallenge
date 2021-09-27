import requests
import json
from config import HEADERS

GET_PAYMENT_METHODS = "https://checkout-test.adyen.com/v67/paymentMethods"
MAKE_PAYMENT = "https://checkout-test.adyen.com/v67/payments"
GET_PAYMENT_DETAILS = "https://checkout-test.adyen.com/v67/payments/details"


def make_adyen_request(url, payload):
    response = requests.post(url=url, headers=HEADERS, data=json.dumps(payload))
    print(response.text)
    return response.text


def get_payment_methods_available(payload):
    return make_adyen_request(GET_PAYMENT_METHODS, payload)


def make_payment(payload):
    return make_adyen_request(MAKE_PAYMENT, payload)


def get_payment_details(payload):
    return make_adyen_request(GET_PAYMENT_DETAILS, payload)
