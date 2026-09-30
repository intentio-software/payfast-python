## Payfast Python library for Payfast by network API

The PayFast Payments Python Package is a comprehensive library designed to facilitate easy integration of PayFast payment solutions into Python applications. This package simplifies the process of implementing secure payments, subscription management, and transaction handling with the PayFast API.

## Features

- **Easy Setup**: Quick and straightforward setup process to integrate PayFast payments into your application.
- **Secure Payments**: Implements secure payment processing using PayFast's security protocols.
- **Subscription Management**: Manage recurring billing and subscriptions with ease.
- **Transaction Handling**: Robust functions to handle transactions, including payments, refunds, and transaction history.
- **Webhook Support**: Support for PayFast webhooks to receive real-time notifications about payment events.

## Installation

Install the package using pip:

```bash
pip install payfast
```

## Quick Start

### 1. Send a customer to checkout (one-off payment)

```python
from payfast.checkout import build_checkout_fields, build_checkout_url

fields = build_checkout_fields(
    merchant_id='10000100',
    merchant_key='46f0cd694581a',
    passphrase='your_passphrase',
    amount=149.00,  # rands, as a decimal - the checkout form's own convention
    item_name='Test Product',
    return_url='https://example.com/return',
    cancel_url='https://example.com/cancel',
    notify_url='https://example.com/notify',
)
redirect_url = build_checkout_url(fields, sandbox=True)
# redirect the customer's browser to redirect_url
```

### 2. ...or set up a recurring subscription instead

Add `subscription_type=1` plus the recurring fields to `extra` - a
passphrase is required for any subscription checkout, PayFast rejects
subscription signatures without one:

```python
from payfast.checkout import FREQUENCY_MONTHLY, build_checkout_fields, build_checkout_url

fields = build_checkout_fields(
    merchant_id='10000100',
    merchant_key='46f0cd694581a',
    passphrase='your_passphrase',
    amount=149.00,
    item_name='kwikCHAT subscription',
    return_url='https://example.com/return',
    cancel_url='https://example.com/cancel',
    notify_url='https://example.com/notify',
    subscription_type=1,
    recurring_amount=149.00,
    frequency=FREQUENCY_MONTHLY,
    cycles=0,  # 0 = run until cancelled
)
redirect_url = build_checkout_url(fields, sandbox=True)
```

### 3. Verify an inbound ITN (payment notification) webhook

```python
from payfast.itn import verify_itn

is_valid, reasons = verify_itn(
    post_data,          # the raw posted form fields, as a dict, in the order received
    source_ip=request_ip,  # the real TCP source IP of the request
    passphrase='your_passphrase',
    sandbox=True,
    expected={'amount_gross': '149.00'},
)
if not is_valid:
    # reasons is a list of human-readable failure descriptions
    ...
```

### 4. Manage an existing subscription by its token

```python
from payfast.api import PayfastAPI

pf = PayfastAPI(merchant_id='10000100', merchant_key='46f0cd694581a', passphrase='your_passphrase', sandbox=True)

pf.fetch_subscription(token)
pf.pause_subscription(token, cycles=1)
pf.unpause_subscription(token)
pf.update_subscription(token, amount=19900)  # cents, the management API's own convention
pf.cancel_subscription(token)
```

## Configuration

Before making any requests, configure the client with your PayFast merchant details. You can enable sandbox mode for testing purposes.

## Documentation

For detailed documentation on all available methods and their usage, please refer to the official PayFast API documentation.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository issue tracker.
