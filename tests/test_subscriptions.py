from unittest.mock import Mock, patch

from payfast.api import PayfastAPI


def _api() -> PayfastAPI:
    return PayfastAPI(merchant_id="10000100", merchant_key="46f0cd694581a", passphrase="jt7NOE43FZPn")


def test_fetch_subscription_calls_the_fetch_endpoint():
    api = _api()
    with patch.object(api.session, "get", return_value=Mock()) as mock_get:
        api.fetch_subscription("abc-123")
        called_url = mock_get.call_args.args[0]
        assert called_url == "https://api.payfast.co.za/subscriptions/abc-123/fetch"


def test_pause_subscription_sends_cycles_and_uses_put():
    api = _api()
    with patch.object(api.session, "request", return_value=Mock()) as mock_request:
        api.pause_subscription("abc-123", cycles=2)
        method, url = mock_request.call_args.args
        assert method == "put"
        assert url == "https://api.payfast.co.za/subscriptions/abc-123/pause"
        assert mock_request.call_args.kwargs["json"] == {"cycles": 2}


def test_pause_subscription_defaults_to_one_cycle():
    api = _api()
    with patch.object(api.session, "request", return_value=Mock()) as mock_request:
        api.pause_subscription("abc-123")
        assert mock_request.call_args.kwargs["json"] == {"cycles": 1}


def test_unpause_subscription_uses_put_with_no_body():
    api = _api()
    with patch.object(api.session, "request", return_value=Mock()) as mock_request:
        api.unpause_subscription("abc-123")
        method, url = mock_request.call_args.args
        assert method == "put"
        assert url == "https://api.payfast.co.za/subscriptions/abc-123/unpause"
        assert mock_request.call_args.kwargs["json"] == {}


def test_cancel_subscription_uses_put():
    api = _api()
    with patch.object(api.session, "request", return_value=Mock()) as mock_request:
        api.cancel_subscription("abc-123")
        method, url = mock_request.call_args.args
        assert method == "put"
        assert url == "https://api.payfast.co.za/subscriptions/abc-123/cancel"


def test_update_subscription_uses_patch_and_only_sends_given_fields():
    api = _api()
    with patch.object(api.session, "request", return_value=Mock()) as mock_request:
        api.update_subscription("abc-123", amount=19900, frequency=3)
        method, url = mock_request.call_args.args
        assert method == "patch"
        assert url == "https://api.payfast.co.za/subscriptions/abc-123/update"
        assert mock_request.call_args.kwargs["json"] == {"amount": 19900, "frequency": 3}


def test_sandbox_mode_adds_testing_query_param():
    api = PayfastAPI(merchant_id="10000100", merchant_key="46f0cd694581a", sandbox=True)
    with patch.object(api.session, "request", return_value=Mock()) as mock_request:
        api.cancel_subscription("abc-123")
        _, url = mock_request.call_args.args
        assert url == "https://api.payfast.co.za/subscriptions/abc-123/cancel?testing=true"
