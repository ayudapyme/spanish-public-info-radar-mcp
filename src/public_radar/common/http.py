"""HTTP client with retry and timeout support.

This module provides a configured HTTP client for making requests
to external APIs with exponential backoff retry logic.
"""

import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

# Default timeout configuration
DEFAULT_TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=30.0,
    write=10.0,
    pool=10.0,
)

# User agent for requests
USER_AGENT = "PublicRadar/0.1.0 (MCP Server for Spanish Public Data)"


class HttpClientError(Exception):
    """Base exception for HTTP client errors."""

    def __init__(self, message: str, status_code: int | None = None, url: str | None = None) -> None:
        """Initialize HTTP client error.

        :param message: Error message.
        :type message: str
        :param status_code: HTTP status code if available.
        :type status_code: int | None
        :param url: URL that caused the error.
        :type url: str | None
        """
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class NotFoundError(HttpClientError):
    """Raised when a resource is not found (404)."""

    pass


def create_http_client(
    timeout: httpx.Timeout | None = None,
    follow_redirects: bool = True,
) -> httpx.Client:
    """Create a configured HTTP client.

    :param timeout: Custom timeout configuration.
    :type timeout: httpx.Timeout | None
    :param follow_redirects: Whether to follow redirects.
    :type follow_redirects: bool
    :return: Configured HTTP client.
    :rtype: httpx.Client

    Example::

        client = create_http_client()
        response = client.get("https://example.com")
    """
    return httpx.Client(
        timeout=timeout or DEFAULT_TIMEOUT,
        follow_redirects=follow_redirects,
        headers={"User-Agent": USER_AGENT},
    )


def create_async_http_client(
    timeout: httpx.Timeout | None = None,
    follow_redirects: bool = True,
) -> httpx.AsyncClient:
    """Create a configured async HTTP client.

    :param timeout: Custom timeout configuration.
    :type timeout: httpx.Timeout | None
    :param follow_redirects: Whether to follow redirects.
    :type follow_redirects: bool
    :return: Configured async HTTP client.
    :rtype: httpx.AsyncClient

    Example::

        async with create_async_http_client() as client:
            response = await client.get("https://example.com")
    """
    return httpx.AsyncClient(
        timeout=timeout or DEFAULT_TIMEOUT,
        follow_redirects=follow_redirects,
        headers={"User-Agent": USER_AGENT},
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    reraise=True,
)
def fetch_with_retry(
    client: httpx.Client,
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    raise_for_status: bool = True,
) -> httpx.Response:
    """Fetch URL with automatic retry on transient failures.

    Retries up to 3 times with exponential backoff for:
    - Timeout errors
    - Network errors

    :param client: HTTP client to use.
    :type client: httpx.Client
    :param url: URL to fetch.
    :type url: str
    :param method: HTTP method (GET, POST, etc.).
    :type method: str
    :param headers: Additional headers.
    :type headers: dict[str, str] | None
    :param params: Query parameters.
    :type params: dict[str, Any] | None
    :param raise_for_status: Whether to raise on HTTP errors.
    :type raise_for_status: bool
    :return: HTTP response.
    :rtype: httpx.Response
    :raises HttpClientError: On HTTP errors if raise_for_status is True.
    :raises NotFoundError: On 404 responses.

    Example::

        client = create_http_client()
        response = fetch_with_retry(client, "https://api.example.com/data")
    """
    logger.debug("Fetching %s %s", method, url)

    try:
        response = client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
        )

        if raise_for_status:
            if response.status_code == 404:
                raise NotFoundError(
                    f"Resource not found: {url}",
                    status_code=404,
                    url=url,
                )
            response.raise_for_status()

        return response

    except httpx.HTTPStatusError as e:
        logger.warning("HTTP error %d for %s", e.response.status_code, url)
        raise HttpClientError(
            f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
            status_code=e.response.status_code,
            url=url,
        ) from e


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    reraise=True,
)
async def async_fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    raise_for_status: bool = True,
) -> httpx.Response:
    """Async version of fetch_with_retry.

    :param client: Async HTTP client to use.
    :type client: httpx.AsyncClient
    :param url: URL to fetch.
    :type url: str
    :param method: HTTP method.
    :type method: str
    :param headers: Additional headers.
    :type headers: dict[str, str] | None
    :param params: Query parameters.
    :type params: dict[str, Any] | None
    :param raise_for_status: Whether to raise on HTTP errors.
    :type raise_for_status: bool
    :return: HTTP response.
    :rtype: httpx.Response
    """
    logger.debug("Async fetching %s %s", method, url)

    try:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
        )

        if raise_for_status:
            if response.status_code == 404:
                raise NotFoundError(
                    f"Resource not found: {url}",
                    status_code=404,
                    url=url,
                )
            response.raise_for_status()

        return response

    except httpx.HTTPStatusError as e:
        logger.warning("HTTP error %d for %s", e.response.status_code, url)
        raise HttpClientError(
            f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
            status_code=e.response.status_code,
            url=url,
        ) from e


def download_file(
    client: httpx.Client,
    url: str,
    dest_path: str,
    chunk_size: int = 8192,
) -> int:
    """Download a file to disk with streaming.

    :param client: HTTP client to use.
    :type client: httpx.Client
    :param url: URL to download.
    :type url: str
    :param dest_path: Destination file path.
    :type dest_path: str
    :param chunk_size: Size of chunks to write.
    :type chunk_size: int
    :return: Total bytes downloaded.
    :rtype: int

    Example::

        client = create_http_client()
        size = download_file(client, "https://example.com/file.zip", "/tmp/file.zip")
    """
    logger.info("Downloading %s to %s", url, dest_path)
    total_bytes = 0

    with client.stream("GET", url) as response:
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                f.write(chunk)
                total_bytes += len(chunk)

    logger.info("Downloaded %d bytes to %s", total_bytes, dest_path)
    return total_bytes
