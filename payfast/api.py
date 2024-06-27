from datetime import datetime
import hashlib
from typing import Optional
import urllib.parse
from pydantic import BaseModel, ValidationError
import pytz
import requests


class PayfastHeaders(BaseModel):
    merchant_id: int
    version: str
    timestamp: str


class PayfastBodyTokenization(BaseModel):
    amount: int
    item_name: str
    item_description: Optional[str]
    itn: Optional[bool] = True
    m_payment_id: Optional[str]
    cc_cvv: Optional[int]
    setup: Optional[str]


class PayfastAPI:
    def __init__(
        self, merchant_id: str, merchant_key: str, passphrase: str = "", sandbox=False
    ):
        self.merchant_id = merchant_id
        self.merchant_key = merchant_key
        self.passphrase = passphrase
        self.test_sandbox_mode = sandbox
        self.session = requests.Session()

    def _generate_headers(self) -> dict:
        # Generate the headers for the Payfast API
        return {
            "merchant-id": self.merchant_id,
            "version": "v1",
            "timestamp": datetime.now(pytz.timezone("Africa/Johannesburg")).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
        }

    def _generate_signature(self, data: dict):
        # Generate a signature using the merchant_key
        payload = ""
        if self.passphrase != "":
            data["passphrase"] = self.passphrase
        sortedData = sorted(data)
        for key in sortedData:
            # Get all the data from Payfast and prepare parameter string
            payload += (
                key
                + "="
                + urllib.parse.quote_plus(str(data[key]).replace("+", " "))
                + "&"
            )
        # After looping through, cut the last & or append your passphrase
        payload = payload[:-1]
        return hashlib.md5(payload.encode()).hexdigest()

    def _request_get(self, path: str, query_params: dict) -> requests.Response:
        # Make a GET request to the Payfast API
        headers = self._generate_headers()
        # Add the signature to the headers
        headers["signature"] = self._generate_signature(headers)

        if self.test_sandbox_mode:
            query_params["testing"] = True

        return self.session.get(
            f"https://api.payfast.co.za/{path}",
            headers=headers,
            params=query_params,
        )

    def _request_post(self, path: str, body_data: dict) -> requests.Response:
        # Make a POST request to the Payfast API
        headers = self._generate_headers()
        # Add the signature to the headers
        signature_payload = {**headers, **body_data}
        headers["signature"] = self._generate_signature(signature_payload)

        query_params = {}
        query_params_encoded = ""

        if self.test_sandbox_mode:
            query_params["testing"] = "true"
            query_params_encoded = "?" + urllib.parse.urlencode(query_params)

        return self.session.post(
            f"https://api.payfast.co.za/{path}{query_params_encoded}",
            headers=headers,
            json=body_data,
        )

    def charge_tokenization_payment(self, token: str, payload: dict):
        # check to see if the schema is valid

        try:
            validated_payload = PayfastBodyTokenization(**payload)

            try:
                response = self._request_post(
                    f"subscriptions/{token}/adhoc", validated_payload.dict()
                )
                return response
            except Exception as e:
                print(f"Request error: {e}")
                raise e

        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e
