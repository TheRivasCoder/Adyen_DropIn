from flask import Flask, render_template, request
from configparser import RawConfigParser
import Adyen
import json

app = Flask(__name__)

# Merchant key, api key, and client key from Adyen
merchant_account = 'YOUR_MERCHANT_ACCOUNT'
checkout_apikey = 'YOUR_API_KEY'
client_key = 'YOUR_CLIENT_KEY'

# Route for Home
@app.route("/")
def home():
    if (client_key == 'exampleKey'):
        abort("Unable to start, config.ini is not updated to actual params. ")
    return render_template("home.html", title="Demo Store")

# Route for Checkout
@app.route('/checkout')
def checkout():
    paymentMethods = getPaymentMethods()
    return render_template('checkout.html', 
        title="Checkout",
        paymentMethods=paymentMethods, 
        clientKey=client_key)

# Route for Application Payment Request API (with drop-in Event Data)
@app.route('/payments/payment', methods=['POST'])
def payments():
    paymentResponse = sendPayment(request.get_json()) # Response to SendPayment
    return paymentResponse

# Route for redirectHandler
@app.route('/redirectHandler')
def orderRedirectHandler():
    # Load the payload from the URL parameters and pass to getPaymentsDetails to get the payment results
    redirectedPaymentDetails = getPaymentsDetails(request.args.get('payload'))
    
    if (redirectedPaymentDetails['resultCode'].lower() == 'authorised' or
        redirectedPaymentDetails['resultCode'].lower() == 'received'): 
        return render_template('success.html', 
            resultCode=redirectedPaymentDetails['resultCode'],
            merchantReference=redirectedPaymentDetails['merchantReference'],
            pspReference=redirectedPaymentDetails['pspReference'],
            paymentMethod=redirectedPaymentDetails['paymentMethod']
        )
    else:
        return render_template('failure.html')

# Route for order Success
@app.route('/success')
def orderSuccess():
    return render_template('success.html', 
        resultCode=request.args.get('resultCode'),
        merchantReference=request.args.get('merchantReference'),
        pspReference=request.args.get('pspReference'),
        title="Your Order Was Successful!"  )

# Route for order failure
@app.route('/failed')
def orderFailed():
    return render_template('failure.html',
        title="An Error Occurred"  )

# Route for Application Payment Details Request API (with drop-in Event Data). Required during redirect. 
@app.route('/payments/details', methods=['POST'])
def paymentDetails():
    paymentDetails = getPaymentsDetails(request.get_json())
    return paymentDetails


def getPaymentMethods():
    '''
        getPaymentMethods(): Triggers Adyen Function to sent request the available Payment Methods from the Merchant Account.
        
        Returns a serialised JSON string of the available Payment Methods. 
    '''
    adyen = Adyen.Adyen()
    adyen.payment.client.platform = "test"
    adyen.client.xapikey = checkout_apikey
    
    request = {
        'merchantAccount': merchant_account,
        'countryCode': 'AU',
        'shopperLocale': 'en-AU',
        'amount': {
            'value': 4000,
            'currency': 'AUD'
        },
        'channel': 'Web'
    }
    # Print the Payment Methods request
    print("Adyen Payment Methodsrequest:\n" + str(request)  + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    # Adyen.checkout.payment_methods response is TYPE AdyenResult
    paymentMethodsResult = adyen.checkout.payment_methods(request)
    
    # Response needs to be formated (includes: "True" -- bad JSON!) json loads and dump handles this
    formattedResult = json.loads(paymentMethodsResult.raw_response)
    paymentMethodsStr = json.dumps(formattedResult)

    # Print the Payment Methods response
    print("Adyen Payment Methods response:\n" + paymentMethodsStr + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")    
    return paymentMethodsStr

def sendPayment(stateData):  
    '''
        sendPayment(stateData): Triggers Adyen Function to sent the Payment request from the Drop-In Input event.
        
        Returns: Serialised JSON String from the Adyen Payments request
    '''
    adyen = Adyen.Adyen()
    adyen.payment.client.platform = "test"
    adyen.client.xapikey = checkout_apikey

    # TROUBLES: had issues with double nesting: paymentMethod: paymentMethod: {} resulting in "422" validation error
    paymentMethod = stateData['paymentMethod']
    
    paymentsRequest = {
        'merchantAccount': merchant_account,
        'paymentMethod': paymentMethod, 
        'amount': {
            'value': 4000,
            'currency': 'AUD'
        },
        'reference': 'matthew_checkoutChallenge',  # Challenge condition "{yourFirstName}_checkoutChallenge"
        "channel": "web",
		'returnUrl': "http://localhost:5000/redirectHandler",
        "additionalData": { "allow3DS2": "true"},  # Needed, otherwise, 3DS2 will not run
        "origin": "http://localhost:5000", # Needed, otherwise, 3DS2 will not run
    }
    # Isolating browser info from stateData to feed for 3DS2 Authentication
    # BrowserInfo is not available for Local Payment, should only be added if Credit Card Payment Method
    if (paymentMethod['type'] == "scheme"):
        paymentsRequest['browserInfo'] = stateData['browserInfo']

    #Print Adyen Payments request
    print("Adyen Payments request:\n" + str(paymentsRequest) + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    paymentsResult = adyen.checkout.payments(paymentsRequest)
    paymentsResultStr = json.dumps(paymentsResult.message) # TROUBLES: bad json ' instead of "

    # Print the Payments response
    print("Adyen Payments response:\n" + paymentsResultStr  + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    # Pass the result back to the frontend
    return paymentsResultStr

def getPaymentsDetails(payLoad):  
    '''
        getPaymentsDetails(payLoad): Triggers Adyen Function to sent the Payments Details, as a follow-up to a redirect,
        Or as a follow-up to an intermidate action performed by the user (e.g. 3DS or QR-Code)
        
        Returns: A Python Dictionary object (converted from a JSON object), from the Adyen Payments Details Response
        2 expected uses: 
            [1] From a Local Payment Method redirect, needed details
            [2] From a 3DS Credit Card Payment with 3D Secure2 authentication
    '''
    adyen = Adyen.Adyen()
    adyen.payment.client.platform = "test"
    adyen.client.xapikey = checkout_apikey
    
    # TROUBLES: validation error when sending Details request, to be reformatted like so
    # TROUBLES: Each use case will provide the payLoad differently. 
    if ( 'details' in payLoad ): 
        paymentsDetailsRequest = payLoad
    else:
        paymentsDetailsRequest = { 'details': { 'payload': payLoad } }
    
    # Print the Payments Details Request
    print("Adyen Payments Details request:\n" + str(paymentsDetailsRequest) + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    paymentsDetailsResult = adyen.checkout.payments_details(paymentsDetailsRequest)
    paymentsDetailsResultStr = json.dumps(paymentsDetailsResult.message)  # TROUBLES: bad json ' instead of "

    # Print the Payments Details response
    print("Adyen Payments Details response:\n" + paymentsDetailsResultStr  + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    # Pass the result back to the frontend needs to be in python Dict format (not JSON Str)
    paymentsDetailsDict = json.loads(paymentsDetailsResultStr)
    return paymentsDetailsDict

if __name__ == '__main__':
    app.run()