from flask import Flask, render_template, request
import json
import uuid

from config import CLIENT_KEY, MERCHANT_ACCOUNT
from webfunctions import GET_PAYMENT_METHODS, GET_PAYMENT_DETAILS, MAKE_PAYMENT, make_adyen_request

def chosen_country(country):
    if country == "SG":
        return {'value':2698, "currency":'SGD'}
    elif country == "CN":
        return {'value':2698, "currency":'CNY'}
    elif country == "AU":
        return {'value':2698, "currency":'AUD'}
    else:
        return {'value':2698, "currency":'EUR'}

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
    print(country_code)
    return render_template('adyen_component.html', client_key=CLIENT_KEY, country_code=country_code)


@app.route('/api/getPaymentMethods', methods=['GET', 'POST'])
def get_payment_methods():
    payment_info = request.get_json()
    order_ref = str(uuid.uuid4())
    print(payment_info)
    payload = {
        'merchantAccount': MERCHANT_ACCOUNT,
        'countryCode': payment_info['chosenCountry'],
        'amount': chosen_country(payment_info['chosenCountry']),
        'channel': 'Web'
    }
    return make_adyen_request(GET_PAYMENT_METHODS, payload)


@app.route('/api/initiatePayment', methods=['GET', 'POST'])
def initiate_payment():
    payment_info = request.get_json()
    order_ref = str(uuid.uuid4())
    print(payment_info)

    if (payment_info["paymentMethod"]['type'] == "scheme"):
        payments_request = {
            'amount': {
                'value': 2698,
                'currency': 'EUR'
            },
            'paymentMethod': (payment_info["paymentMethod"]),
            'reference': order_ref,
            'channel': 'web',
            'countryCode':'NL',
            'billingAddress': payment_info['billingAddress'],
            'browserInfo': payment_info['browserInfo'],
            'returnUrl': "https://fathomless-castle-02164.herokuapp.com/api/handleRedirect",
            'origin': 'https://fathomless-castle-02164.herokuapp.com/',
            'merchantAccount': MERCHANT_ACCOUNT,
            'additionalData': {"allow3DS2": "true"}
        }
    elif(payment_info["paymentMethod"]['type'] == "alipay"):
        payments_request = {
            'amount': {
                'value': 2700,
                'currency': 'CNY'
            },
            'paymentMethod': (payment_info["paymentMethod"]),
            'reference': order_ref,
            'channel': 'web',
            'countryCode': "CN",
            'returnUrl': "https://fathomless-castle-02164.herokuapp.com/api/handleRedirect",
            'merchantAccount': MERCHANT_ACCOUNT
        }
    elif(payment_info["paymentMethod"]['type'] == "poli"):
        payments_request = {
            'amount': {
                'value': 2700,
                'currency': 'AUD'
            },
            'paymentMethod': (payment_info["paymentMethod"]),
            'reference': order_ref,
            'channel': 'web',
            'countryCode': "AU",
            'returnUrl': "https://fathomless-castle-02164.herokuapp.com/api/handleRedirect",
            'merchantAccount': MERCHANT_ACCOUNT
        }
    else:
        payments_request = {
            'amount': {
                'value': 2698,
                'currency': 'EUR'
            },
            'paymentMethod': (payment_info["paymentMethod"]),
            'reference': order_ref,
            'channel': 'web',
            'countryCode': "NL",
            'returnUrl': "https://fathomless-castle-02164.herokuapp.com/api/handleRedirect",
            'merchantAccount': MERCHANT_ACCOUNT
        }

    return make_adyen_request(MAKE_PAYMENT, payments_request)


@app.route('/api/makeDetailsCall', methods=['GET', 'POST'])
def payment_details():
    values = request.get_json()
    return make_adyen_request(GET_PAYMENT_DETAILS, values)


@app.route('/api/handleRedirect', methods=['GET'])
def handle_redirect():
    id = request.args['redirectResult']
    body = {
        "details": {
            "redirectResult": id
        }
    }
    payments_response = make_adyen_request(GET_PAYMENT_DETAILS, body)
    print(json.loads(payments_response)['resultCode'])
    if json.loads(payments_response)['resultCode'] == "Authorised" or json.loads(payments_response)['resultCode'] == "Pending" or json.loads(payments_response)['resultCode'] == "Received":
        return render_template("checkout_success.html", responseJson=payments_response)
    elif json.loads(payments_response)['resultCode'] == "Refused" or json.loads(payments_response)['resultCode'] == "Cancelled" or json.loads(payments_response)['resultCode'] == "Error":
        return render_template("checkout_failed.html", responseJson=payments_response)


if __name__ == '__main__':
    app.run()
