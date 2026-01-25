"""Unit tests for HTTP client utilities."""

from unittest.mock import MagicMock

import httpx
import pytest

from public_radar.common.http import (
    DEFAULT_TIMEOUT,
    USER_AGENT,
    HttpClientError,
    NotFoundError,
    create_http_client,
    fetch_with_retry,
)


class TestHttpClientError:
    """Tests for HttpClientError exception."""

    def test_creates_with_message(self) -> None:
        """Should create error with message."""
        err = HttpClientError("Test error")
        assert str(err) == "Test error"
        assert err.status_code is None
        assert err.url is None

    def test_creates_with_all_fields(self) -> None:
        """Should create error with all fields."""
        err = HttpClientError("Test error", status_code=500, url="http://example.com")
        assert str(err) == "Test error"
        assert err.status_code == 500
        assert err.url == "http://example.com"


class TestNotFoundError:
    """Tests for NotFoundError exception."""

    def test_is_subclass_of_http_client_error(self) -> None:
        """Should be subclass of HttpClientError."""
        err = NotFoundError("Not found", status_code=404)
        assert isinstance(err, HttpClientError)
        assert err.status_code == 404


class TestDefaultTimeout:
    """Tests for default timeout configuration."""

    def test_has_expected_values(self) -> None:
        """Should have expected timeout values."""
        assert DEFAULT_TIMEOUT.connect == 10.0
        assert DEFAULT_TIMEOUT.read == 30.0
        assert DEFAULT_TIMEOUT.write == 10.0
        assert DEFAULT_TIMEOUT.pool == 10.0


class TestUserAgent:
    """Tests for user agent string."""

    def test_contains_product_name(self) -> None:
        """Should contain product name."""
        assert "PublicRadar" in USER_AGENT

    def test_contains_version(self) -> None:
        """Should contain version."""
        assert "0.1.0" in USER_AGENT


class TestCreateHttpClient:
    """Tests for create_http_client function."""

    def test_creates_client_with_defaults(self) -> None:
        """Should create client with default settings."""
        client = create_http_client()
        try:
            assert client.timeout == DEFAULT_TIMEOUT
            assert client.headers["User-Agent"] == USER_AGENT
        finally:
            client.close()

    def test_creates_client_with_custom_timeout(self) -> None:
        """Should create client with custom timeout."""
        custom_timeout = httpx.Timeout(5.0)
        client = create_http_client(timeout=custom_timeout)
        try:
            assert client.timeout == custom_timeout
        finally:
            client.close()

    def test_creates_client_with_redirect_setting(self) -> None:
        """Should respect follow_redirects setting."""
        client = create_http_client(follow_redirects=False)
        try:
            assert client.follow_redirects is False
        finally:
            client.close()


class TestFetchWithRetry:
    """Tests for fetch_with_retry function."""

    def test_returns_response_on_success(self) -> None:
        """Should return response on successful request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.return_value = mock_response

        result = fetch_with_retry(mock_client, "http://example.com")

        assert result == mock_response
        mock_client.request.assert_called_once()

    def test_raises_not_found_error_on_404(self) -> None:
        """Should raise NotFoundError on 404."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.return_value = mock_response

        with pytest.raises(NotFoundError) as exc_info:
            fetch_with_retry(mock_client, "http://example.com/missing")

        assert exc_info.value.status_code == 404
        assert "example.com/missing" in exc_info.value.url

    def test_raises_http_client_error_on_other_errors(self) -> None:
        """Should raise HttpClientError on HTTP errors."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500, reason_phrase="Internal Server Error"),
        )

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.return_value = mock_response

        with pytest.raises(HttpClientError) as exc_info:
            fetch_with_retry(mock_client, "http://example.com")

        assert exc_info.value.status_code == 500

    def test_skips_status_check_when_disabled(self) -> None:
        """Should skip status check when raise_for_status=False."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.return_value = mock_response

        result = fetch_with_retry(mock_client, "http://example.com", raise_for_status=False)

        assert result == mock_response

    def test_passes_headers(self) -> None:
        """Should pass custom headers."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.return_value = mock_response

        custom_headers = {"Accept": "application/json"}
        fetch_with_retry(mock_client, "http://example.com", headers=custom_headers)

        mock_client.request.assert_called_once()
        call_kwargs = mock_client.request.call_args.kwargs
        assert call_kwargs["headers"] == custom_headers

    def test_passes_params(self) -> None:
        """Should pass query parameters."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.return_value = mock_response

        params = {"page": 1, "limit": 10}
        fetch_with_retry(mock_client, "http://example.com", params=params)

        mock_client.request.assert_called_once()
        call_kwargs = mock_client.request.call_args.kwargs
        assert call_kwargs["params"] == params

    def test_uses_specified_method(self) -> None:
        """Should use specified HTTP method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.return_value = mock_response

        fetch_with_retry(mock_client, "http://example.com", method="POST")

        mock_client.request.assert_called_once()
        call_kwargs = mock_client.request.call_args.kwargs
        assert call_kwargs["method"] == "POST"


class TestRetryBehavior:
    """Tests for retry behavior."""

    def test_retries_on_timeout(self) -> None:
        """Should retry on timeout exceptions."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.side_effect = [
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            MagicMock(status_code=200),
        ]

        result = fetch_with_retry(mock_client, "http://example.com")

        assert result.status_code == 200
        assert mock_client.request.call_count == 3

    def test_retries_on_network_error(self) -> None:
        """Should retry on network errors."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client.request.side_effect = [
            httpx.NetworkError("Network error"),
            mock_response,
        ]

        result = fetch_with_retry(mock_client, "http://example.com")

        assert result.status_code == 200
        assert mock_client.request.call_count == 2

    def test_gives_up_after_max_retries(self) -> None:
        """Should give up after max retries."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_client.request.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(httpx.TimeoutException):
            fetch_with_retry(mock_client, "http://example.com")

        # Default is 3 attempts
        assert mock_client.request.call_count == 3
