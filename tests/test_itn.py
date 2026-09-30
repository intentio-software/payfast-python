from unittest.mock import Mock, patch

from payfast.itn import (
    confirm_with_payfast,
    verify_expected_data,
    verify_itn,
    verify_signature,
    verify_source_ip,
)

SAMPLE_ITN = {
    "m_payment_id": "tenant-42-cycle-1",
    "pf_payment_id": "987654321",
    "payment_status": "COMPLETE",
    "item_name": "kwikCHAT subscription",
    "amount_gross": "149.00",
}


def _signed(passphrase: str = "") -> dict:
    from payfast.itn import _itn_signature

    data = dict(SAMPLE_ITN)
    data["signature"] = _itn_signature(data, passphrase)
    return data


def test_verify_signature_accepts_a_correctly_signed_payload():
    assert verify_signature(_signed()) is True


def test_verify_signature_rejects_a_tampered_amount():
    data = _signed()
    data["amount_gross"] = "0.01"
    assert verify_signature(data) is False


def test_verify_signature_rejects_missing_signature():
    assert verify_signature(dict(SAMPLE_ITN)) is False


def test_verify_signature_requires_matching_passphrase():
    data = _signed(passphrase="correct-horse")
    assert verify_signature(data, passphrase="wrong-passphrase") is False
    assert verify_signature(data, passphrase="correct-horse") is True


def test_verify_expected_data_flags_amount_mismatch_beyond_tolerance():
    errors = verify_expected_data(SAMPLE_ITN, {"amount_gross": "999.00"})
    assert errors and "amount_gross" in errors[0]


def test_verify_expected_data_tolerates_float_rounding():
    errors = verify_expected_data(SAMPLE_ITN, {"amount_gross": "149.001"})
    assert errors == []


def test_verify_expected_data_flags_other_field_mismatches():
    errors = verify_expected_data(SAMPLE_ITN, {"payment_status": "FAILED"})
    assert errors and "payment_status" in errors[0]


def test_verify_source_ip_accepts_a_resolved_payfast_address():
    with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("197.97.145.145", 0))]):
        assert verify_source_ip("197.97.145.145") is True


def test_verify_source_ip_rejects_an_unrelated_address():
    with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("197.97.145.145", 0))]):
        assert verify_source_ip("8.8.8.8") is False


def test_confirm_with_payfast_true_only_on_exact_valid_body():
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, text="VALID")
        assert confirm_with_payfast(_signed()) is True

        mock_post.return_value = Mock(ok=True, text="INVALID")
        assert confirm_with_payfast(_signed()) is False


def test_verify_itn_short_circuits_before_the_network_call_on_bad_signature():
    tampered = _signed()
    tampered["amount_gross"] = "0.01"
    with patch("requests.post") as mock_post:
        is_valid, reasons = verify_itn(tampered, source_ip="1.2.3.4")
        assert is_valid is False
        assert "signature mismatch" in reasons
        mock_post.assert_not_called()


def test_verify_itn_passes_when_every_check_succeeds():
    data = _signed()
    with (
        patch("payfast.itn.verify_source_ip", return_value=True),
        patch("payfast.itn.confirm_with_payfast", return_value=True),
    ):
        is_valid, reasons = verify_itn(data, source_ip="197.97.145.145")
        assert is_valid is True
        assert reasons == []
