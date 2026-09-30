"""Signature values below are cross-checked against PayFast's own official
PHP SDK (PayFast\\Auth::generateSignature), run directly as an independent
oracle - not derived from this Python code, so an accidental algorithm
error here would actually be caught rather than just agreeing with itself.
"""

import pytest

from payfast.checkout import build_checkout_fields, build_checkout_signature, build_checkout_url

BASE_DATA = {
    "merchant_id": "10000100",
    "merchant_key": "46f0cd694581a",
    "return_url": "https://example.com/return",
    "cancel_url": "https://example.com/cancel",
    "notify_url": "https://example.com/notify",
    "name_first": "Jane",
    "email_address": "jane@example.com",
    "m_payment_id": "tenant-42-cycle-1",
    "amount": "149.00",
    "item_name": "kwikCHAT subscription",
}


def test_signature_matches_official_sdk_without_passphrase():
    assert build_checkout_signature(dict(BASE_DATA)) == "608a382800f5e58c18aa09eaf90ea663"


def test_signature_matches_official_sdk_with_passphrase():
    assert (
        build_checkout_signature(dict(BASE_DATA), "jt7NOE43FZPn")
        == "ec9728ce40c42a06937074e11dba23cc"
    )


def test_signature_matches_official_sdk_for_a_subscription_with_zero_cycles():
    # cycles=0 means "run until cancelled" in PayFast's own convention, and
    # is excluded from the signature by their SDK (PHP's empty(0) is true) -
    # a real, verified quirk, not a guess.
    data = dict(BASE_DATA)
    data.update(subscription_type=1, recurring_amount="149.00", frequency=3, cycles=0)
    assert build_checkout_signature(data, "jt7NOE43FZPn") == "31177e4be3519a1a69108f47b30c0846"


def test_signature_ignores_field_order_since_it_uses_a_fixed_canonical_order():
    reordered = dict(reversed(list(BASE_DATA.items())))
    assert build_checkout_signature(dict(BASE_DATA)) == build_checkout_signature(reordered)


def test_signature_ignores_fields_outside_the_known_list():
    data = dict(BASE_DATA)
    data["unrecognized_field"] = "should not affect the signature"
    assert build_checkout_signature(dict(BASE_DATA)) == build_checkout_signature(data)


def test_subscription_without_passphrase_raises():
    data = dict(BASE_DATA)
    data["subscription_type"] = 1
    with pytest.raises(ValueError, match="passphrase"):
        build_checkout_signature(data)


def test_build_checkout_fields_includes_signature_and_formats_amount_as_rands():
    fields = build_checkout_fields(
        merchant_id="10000100",
        merchant_key="46f0cd694581a",
        amount=149,
        item_name="kwikCHAT subscription",
        return_url="https://example.com/return",
        cancel_url="https://example.com/cancel",
        notify_url="https://example.com/notify",
    )
    assert fields["amount"] == "149.00"
    assert "signature" in fields
    assert fields["signature"] == build_checkout_signature(
        {k: v for k, v in fields.items() if k != "signature"}
    )


def test_build_checkout_url_targets_sandbox_when_requested():
    url = build_checkout_url({"merchant_id": "10000100"}, sandbox=True)
    assert url.startswith("https://sandbox.payfast.co.za/eng/process?")


def test_build_checkout_url_targets_live_by_default():
    url = build_checkout_url({"merchant_id": "10000100"})
    assert url.startswith("https://www.payfast.co.za/eng/process?")
