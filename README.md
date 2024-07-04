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

```python
from payfast.api import PayfastAPI

pf = PayfastAPI(merchant_id='your_merchant_id', merchant_key='your_merchant_key', passphrase='your_passphrase', sandbox=True)

payment_data = {
    'amount': 100.00,
    'item_name': 'Test Product',
    'item_description': 'A sample product description',
}

response = client.initiate_payment(payment_data)
if response.success:
    print("Payment initiated successfully.")
else:
    print("Payment initiation failed.")
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
