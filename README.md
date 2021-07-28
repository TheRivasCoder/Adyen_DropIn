# Adyen_DropIn

Adyen_DropIn is a small light weight Python application, written using the Flask python framework as an exercise to explore the [Adyen Payment Gateway Drop-In Integration Method](https://docs.adyen.com/checkout/drop-in-web)


##### Supported/Tested Scenarios:
1. Credit Card (Visa - Without 3DS2)
2. Credit Card (Mastercard - Without 3DS2)
3. Local Payment - alipay Payment
4. Local Payment - POLi Payment
6. Credit Card (Visa - 3DS2 (4917 XXXX XXXX XXXX))
7. Credit Card (Mastercard - 3DS2 (5454 XXXX XXXX XXXX))

## Installation

### Step 1

Move inside in the root directory of the application:
```
./Adyen_DropIn/                 // <-- ROOT directory
├── README.md
├── app.py/
├── static/
│   ├── css/
│   │    └── main.css
│   └──img/
│       ├── favicon.ico
│       ├── shopping-bag.svg
│       ├── t-shirt.svg
│       ├── tick.svg
│       └── wrong.svg
├── templates/
│       ├── base.html
│       ├── checkout.html
│       ├── failure.html
│       ├── home.html
│       └── success.html
├── requirements.txt
├── run.sh
└── setup.sh
```

### Step 2

Run setup.sh: this creates a virtual environment, activate the environment and use the package manager [pip3](https://pip.pypa.io/en/stable/) to install the requirements.txt.

```bash
source ./setup.sh
```

### Step 3
Run virtual environment 'activate': 
```bash
. venv/bin/activate
```
### Step 4
Update the 'app.py' file with the with your specific merchant_account, checkout_apikey, and client_key values:
```bash
# Important replace with your own values 
merchant_account = 'YOUR_MERCHANT_ACCOUNT'
checkout_apikey = 'YOUR_API_KEY'
client_key = 'YOUR_CLIENT_KEY'
```

## Usage
Simply run the main project from the bash script:
```bash
source ./run.sh
```
And navigate to [http://localhost:5000](http://localhost:5000)

For test cards see article: [Adyen Test Cards](https://docs.adyen.com/development-resources/test-cards/test-card-numbers#credit-and-debit-cards)
