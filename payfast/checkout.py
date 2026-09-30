"""Hosted checkout (process.payfast.co.za) payment/subscription form building.

This is PayFast's "Custom Integration": redirect the customer to PayFast's
own hosted page (built from a signed set of fields), where they enter card
details and PayFast redirects them back afterward. Separate from api.py's
PayfastAPI, which talks to the Recurring Billing *management* API
(api.payfast.co.za) for an already-created subscription token - this module
is what actually creates that token in the first place.

PayFast's checkout signature is neither alphabetically sorted (that's the
Recurring Billing API's own scheme in api.py) nor "whatever order the
caller passed fields in" - it is computed over a fixed, documented field
order, confirmed against PayFast's own official PHP SDK
(PayFast\\Auth::generateSignature).
"""

import hashlib
import urllib.parse

LIVE_BASE_URL = "https://www.payfast.co.za"
SANDBOX_BASE_URL = "https://sandbox.payfast.co.za"

# PayFast's documented frequency codes for subscription_type=1 (recurring
# billing) - not applicable to subscription_type=2 (tokenization only, no
# fixed schedule, charged ad hoc via PayfastAPI.charge_tokenization_payment).
FREQUENCY_MONTHLY = 3
FREQUENCY_QUARTERLY = 4
FREQUENCY_BIANNUAL = 5
FREQUENCY_ANNUAL = 6

# Fixed field order the signature is computed over - fields not present in
# the caller's data are simply skipped, not treated as empty. Order matters:
# this must match PayFast's own signing order exactly, or every checkout
# will fail signature validation on PayFast's side (rejected before the
# customer ever sees a payment form).
_SIGNATURE_FIELD_ORDER = (
    "merchant_id",
    "merchant_key",
    "return_url",
    "cancel_url",
    "notify_url",
    "notify_method",
    "name_first",
    "name_last",
    "email_address",
    "cell_number",
    "m_payment_id",
    "amount",
    "item_name",
    "item_description",
    "custom_int1",
    "custom_int2",
    "custom_int3",
    "custom_int4",
    "custom_int5",
    "custom_str1",
    "custom_str2",
    "custom_str3",
    "custom_str4",
    "custom_str5",
    "email_confirmation",
    "confirmation_address",
    "currency",
    "payment_method",
    "subscription_type",
    "billing_date",
    "recurring_amount",
    "frequency",
    "cycles",
    "subscription_notify_email",
    "subscription_notify_webhook",
    "subscription_notify_buyer",
)


def build_checkout_signature(data: dict, passphrase: str = "") -> str:
    """The checkout-form/subscription-setup signature - fixed field order,
    empty values excluded, passphrase appended last if set. PayFast requires
    a passphrase to be configured at all for any subscription_type send
    (recurring or tokenization), so this raises rather than silently
    producing a signature PayFast will reject anyway.
    """
    if data.get("subscription_type") and not passphrase:
        raise ValueError("Subscriptions require a merchant passphrase to be set")

    parts = []
    for key in _SIGNATURE_FIELD_ORDER:
        value = data.get(key)
        # Matches PHP's empty() truthiness, which PayFast's own official SDK
        # uses to decide inclusion - not just None/"", but 0/0.0/False too.
        # Confirmed against it directly: cycles=0 (PayFast's own convention
        # for "run until cancelled") is silently excluded from the
        # signature by their SDK, and a naive None/""-only check here
        # produces a signature PayFast's server rejects.
        if not value:
            continue
        parts.append(f"{key}={urllib.parse.quote_plus(str(value).strip())}")
    if passphrase:
        parts.append(f"passphrase={urllib.parse.quote_plus(passphrase.strip())}")

    param_string = "&".join(parts)
    return hashlib.md5(param_string.encode()).hexdigest()


def build_checkout_fields(
    *,
    merchant_id: str,
    merchant_key: str,
    amount: float,
    item_name: str,
    return_url: str,
    cancel_url: str,
    notify_url: str,
    passphrase: str = "",
    **extra,
) -> dict:
    """Build the full field dict (including signature) ready to render as
    hidden form inputs or urlencode into a redirect. `amount` is rands, as a
    decimal (e.g. 149.00), matching the checkout form's own convention -
    NOT the cents-integer convention the Recurring Billing management API
    (api.py) uses for `amount`/`recurring_amount`. `extra` covers everything
    else the field order recognizes: name_first/name_last/email_address,
    subscription_type/billing_date/recurring_amount/frequency/cycles for a
    recurring subscription, custom_str1-5/custom_int1-5, etc.
    """
    data = {
        "merchant_id": merchant_id,
        "merchant_key": merchant_key,
        "return_url": return_url,
        "cancel_url": cancel_url,
        "notify_url": notify_url,
        "amount": f"{amount:.2f}",
        "item_name": item_name,
        **extra,
    }
    data["signature"] = build_checkout_signature(data, passphrase)
    return data


def build_checkout_url(fields: dict, *, sandbox: bool = False) -> str:
    """A GET-redirect URL encoding every field - the simplest way to hand a
    customer off to PayFast from a backend that isn't server-rendering an
    HTML auto-submit form (e.g. a JSON API behind a JS frontend, which just
    does `window.location.href = redirect_url`)."""
    base_url = SANDBOX_BASE_URL if sandbox else LIVE_BASE_URL
    query = urllib.parse.urlencode(fields, quote_via=urllib.parse.quote_plus)
    return f"{base_url}/eng/process?{query}"
