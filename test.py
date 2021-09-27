from flask import Flask, render_template, request
import json
import uuid

from config import CLIENT_KEY, MERCHANT_ACCOUNT
from webfunctions import get_payment_methods_available, get_payment_details, make_payment


def chosen_country(country):
    if country == "SG":
        return {"currency": 'SGD', "country_code": "SG"}
    elif country == "CN":
        return {"currency": 'CNY', "country_code": "CN"}
    elif country == "AU":
        return {"currency": 'AUD', "country_code": "AU"}
    elif country == "DE":
        return {"currency": 'EUR', "country_code": "DE"}
    else:
        return {"currency": 'EUR', "country_code": "NL"}


app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/', methods=['GET'])
def home():
    return render_template("cart.html")


@app.route('/checkout-success', methods=['GET'])
def checkout_success():
    id = request.args['result']
    return render_template("checkout_success.html", responseJson=id)


@app.route('/checkout-failed', methods=['GET'])
def checkout_failed():
    id = request.args['result']
    return render_template("checkout_failed.html", responseJson=id)


@app.route('/checkout', methods=['GET'])
def checkout():
    country_code = request.args['country']
    amount = request.args['value'].replace(".", "")
    return render_template('adyen_component.html', client_key=CLIENT_KEY,
                           currency=chosen_country(country_code)['currency'], value=amount, country_code=country_code)


@app.route('/api/getPaymentMethods', methods=['GET', 'POST'])
def get_payment_methods():
    payment_info = request.get_json()
    order_ref = str(uuid.uuid4())
    print(payment_info, "ege")
    payload = {
        'merchantAccount': MERCHANT_ACCOUNT,
        'countryCode': payment_info['country_code'],
        'amount': {"value": payment_info['value'], "currency": payment_info['currency']},
        'channel': 'Web'
    }
    return get_payment_methods_available(payload)


@app.route('/api/initiatePayment', methods=['GET', 'POST'])
def initiate_payment():
    payment_info = request.get_json()
    order_ref = str(uuid.uuid4())
    print(payment_info)
    payments_request = {
        'amount': {
            'value': payment_info['value'],
            'currency': payment_info['currency']
        },
        'paymentMethod': (payment_info["paymentMethod"]),
        'reference': order_ref,
        'channel': 'web',
        'countryCode': payment_info['country_code'],
        'returnUrl': "http://127.0.0.1:5000/api/handleRedirect",
        'merchantAccount': MERCHANT_ACCOUNT
    }
    if payment_info["paymentMethod"]['type'] == "scheme":
        payments_request['origin'] = 'http://127.0.0.1:5000/'
        payments_request['additionalData'] = {"allow3DS2": "true"}
        payments_request['billingAddress'] = payment_info['billingAddress'],
        payments_request['browserInfo'] = payment_info['browserInfo']

    return make_payment(payments_request)


@app.route('/api/makeDetailsCall', methods=['GET', 'POST'])
def payment_details():
    values = request.get_json()
    print(values)
    return get_payment_details(values)


@app.route('/api/handleRedirect', methods=['GET'])
def handle_redirect():
    id = request.args['redirectResult']
    body = {
        "details": {
            "redirectResult": id
        }
    }
    payments_response = get_payment_details(body)
    print(json.loads(payments_response)['resultCode'])
    if json.loads(payments_response)['resultCode'] == "Authorised" or json.loads(payments_response)[
        'resultCode'] == "Pending" or json.loads(payments_response)['resultCode'] == "Received":
        return render_template("checkout_success.html", responseJson=payments_response)
    elif json.loads(payments_response)['resultCode'] == "Refused" or json.loads(payments_response)[
        'resultCode'] == "Cancelled" or json.loads(payments_response)['resultCode'] == "Error":
        return render_template("checkout_failed.html", responseJson=payments_response)


if __name__ == '__main__':
    app.run()
