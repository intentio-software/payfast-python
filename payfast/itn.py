"""ITN (Instant Transaction Notification) webhook verification.

PayFast POSTs payment/subscription events to your notify_url. This
implements the same four checks PayFast's own official PHP SDK performs
(PayFast\\PaymentIntegrations\\Notification), confirmed against its source:
signature match, source authenticity, expected-data match, and a
server-to-server confirmation callback - all four must pass before the
notification is trusted.

Unlike the checkout signature (checkout.py, fixed field order) or the
Recurring Billing API signature (api.py, alphabetically sorted), the ITN
signature is computed over the fields in whatever order they were
*received* - which is safe because it's PayFast itself that both produces
and later re-derives that order, we're just replaying it back.
"""

import hashlib
import socket
import urllib.parse

import requests

from .checkout import LIVE_BASE_URL, SANDBOX_BASE_URL

# PayFast's own hostnames, re-resolved at verification time rather than
# hardcoded to IP ranges (which PayFast can and does change) - same
# approach as the official SDK's pfValidIP, applied to the actual TCP
# source IP of the request instead of a spoofable Referer header.
_VALID_HOSTNAMES = (
    "www.payfast.co.za",
    "sandbox.payfast.co.za",
    "w1w.payfast.co.za",
    "w2w.payfast.co.za",
)


def _itn_signature(post_data: dict, passphrase: str = "") -> str:
    # Stops entirely at the first "signature" key, matching PayFast's own
    # SDK exactly (PHP's dataToString does `break`, not skip-and-continue) -
    # equivalent in practice since PayFast always sends signature last, but
    # not equivalent in general, so this matches the real behavior rather
    # than one that merely usually agrees with it.
    parts = []
    for key, value in post_data.items():
        if key == "signature":
            break
        parts.append(f"{key}={urllib.parse.quote_plus(str(value))}")
    param_string = "&".join(parts)
    if passphrase:
        param_string += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
    return hashlib.md5(param_string.encode()).hexdigest()


def verify_signature(post_data: dict, passphrase: str = "") -> bool:
    received = post_data.get("signature")
    if not received:
        return False
    return received == _itn_signature(post_data, passphrase)


def verify_source_ip(source_ip: str) -> bool:
    """Resolves PayFast's known hostnames fresh on every call rather than
    trusting a hardcoded IP list - deliberately not cached, since a stale
    cache is exactly how this check would go quietly wrong."""
    valid_ips: set[str] = set()
    for hostname in _VALID_HOSTNAMES:
        try:
            valid_ips.update(
                info[4][0] for info in socket.getaddrinfo(hostname, None)
            )
        except socket.gaierror:
            continue
    return source_ip in valid_ips


def verify_expected_data(post_data: dict, expected: dict) -> list[str]:
    """Returns a list of mismatch descriptions (empty = all matched).
    `amount_gross` is compared with a small float tolerance (PayFast's own
    SDK uses 0.01) since it arrives as a formatted decimal string."""
    errors = []
    for key, expected_value in expected.items():
        actual_value = post_data.get(key)
        if key == "amount_gross":
            try:
                if abs(float(expected_value) - float(actual_value)) > 0.01:
                    errors.append(
                        f"amount_gross is {actual_value!r}, expected {expected_value!r}"
                    )
            except (TypeError, ValueError):
                errors.append(f"amount_gross is {actual_value!r}, not a number")
        elif actual_value != expected_value:
            errors.append(f"{key} is {actual_value!r}, expected {expected_value!r}")
    return errors


def confirm_with_payfast(post_data: dict, *, sandbox: bool = False, timeout: int = 15) -> bool:
    """The required server-to-server round trip: PayFast expects the exact
    same signed param string posted back to it, and responds with the
    literal body "VALID" if (and only if) it recognizes this as a
    notification it actually sent."""
    parts = []
    for key, value in post_data.items():
        if key == "signature":
            break
        parts.append(f"{key}={urllib.parse.quote_plus(str(value))}")
    param_string = "&".join(parts)

    base_url = SANDBOX_BASE_URL if sandbox else LIVE_BASE_URL
    resp = requests.post(
        f"{base_url}/eng/query/validate",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data=param_string.encode(),
        timeout=timeout,
    )
    return resp.ok and resp.text.strip() == "VALID"


def verify_itn(
    post_data: dict,
    source_ip: str,
    *,
    passphrase: str = "",
    sandbox: bool = False,
    expected: dict | None = None,
) -> tuple[bool, list[str]]:
    """Runs all four checks, returns (is_valid, reasons) - reasons is
    non-empty whenever is_valid is False, so a caller can log *why* a
    notification was rejected instead of just that it was."""
    reasons: list[str] = []

    if not verify_signature(post_data, passphrase):
        reasons.append("signature mismatch")
    if not verify_source_ip(source_ip):
        reasons.append(f"source IP {source_ip!r} is not a known PayFast address")
    if expected:
        reasons.extend(verify_expected_data(post_data, expected))
    if not reasons and not confirm_with_payfast(post_data, sandbox=sandbox):
        reasons.append("PayFast server confirmation did not return VALID")

    return (len(reasons) == 0, reasons)
