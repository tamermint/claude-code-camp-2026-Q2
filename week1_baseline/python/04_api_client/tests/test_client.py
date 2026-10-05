from __future__ import annotations

import io
import json
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure boukensha is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from boukensha.client import Client
from boukensha.errors import ApiError


class DummyBuilder:
    def __init__(self, url="https://api.example.com/v1/test", headers=None, payload=None):
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        self.payload = payload or {"prompt": "hello"}

    def to_api_payload(self, max_output_tokens=1024):
        return self.payload


def test_client_success():
    client = Client()
    builder = DummyBuilder()

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"result": "success"}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = client.call(builder)
        assert res == {"result": "success"}
    print("✓ test_client_success passed")


def test_client_retryable_status():
    client = Client(max_retries=2, base_retry_delay=0.01)
    builder = DummyBuilder()

    http_429 = urllib.error.HTTPError(
        url=builder.url,
        code=429,
        msg="Too Many Requests",
        hdrs={},
        fp=io.BytesIO(b'{"error": "rate limit"}'),
    )

    mock_success = MagicMock()
    mock_success.read.return_value = json.dumps({"result": "recovered"}).encode("utf-8")
    mock_success.__enter__.return_value = mock_success

    # First call raises 429, second call succeeds
    with patch("urllib.request.urlopen", side_effect=[http_429, mock_success]):
        res = client.call(builder)
        assert res == {"result": "recovered"}
    print("✓ test_client_retryable_status passed")


def test_client_fatal_http_error():
    client = Client(max_retries=2, base_retry_delay=0.01)
    builder = DummyBuilder()

    http_400 = urllib.error.HTTPError(
        url=builder.url,
        code=400,
        msg="Bad Request",
        hdrs={},
        fp=io.BytesIO(b'{"error": "invalid parameter"}'),
    )

    with patch("urllib.request.urlopen", side_effect=http_400):
        try:
            client.call(builder)
            assert False, "Should have raised ApiError"
        except ApiError as e:
            assert "(400)" in str(e)
            assert "invalid parameter" in str(e)
    print("✓ test_client_fatal_http_error passed")


def test_client_exhausted_retries():
    client = Client(max_retries=2, base_retry_delay=0.01)
    builder = DummyBuilder()

    http_503 = urllib.error.HTTPError(
        url=builder.url,
        code=503,
        msg="Service Unavailable",
        hdrs={},
        fp=io.BytesIO(b'{"error": "unavailable"}'),
    )

    with patch("urllib.request.urlopen", side_effect=http_503):
        try:
            client.call(builder)
            assert False, "Should have raised ApiError"
        except ApiError as e:
            assert "(503)" in str(e)
            assert "3 attempts" in str(e)
    print("✓ test_client_exhausted_retries passed")


def test_client_transient_network_error():
    client = Client(max_retries=2, base_retry_delay=0.01)
    builder = DummyBuilder()

    conn_error = ConnectionResetError("Connection reset by peer")

    mock_success = MagicMock()
    mock_success.read.return_value = json.dumps({"result": "after_reset"}).encode("utf-8")
    mock_success.__enter__.return_value = mock_success

    with patch("urllib.request.urlopen", side_effect=[conn_error, mock_success]):
        res = client.call(builder)
        assert res == {"result": "after_reset"}
    print("✓ test_client_transient_network_error passed")


if __name__ == "__main__":
    test_client_success()
    test_client_retryable_status()
    test_client_fatal_http_error()
    test_client_exhausted_retries()
    test_client_transient_network_error()
    print("\nAll 5 Client tests passed successfully!")
