from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any, Optional
from .errors import ApiError
from .prompt_builder import PromptBuilder

TRANSIENT_EXCEPTIONS = (
    urllib.error.URLError,
    TimeoutError,
    ConnectionResetError,
    ConnectionRefusedError,
    ssl.SSLError,
    OSError,
)


class Client:
    """Stateless HTTP client for dispatching serialized PromptBuilder payloads to LLM APIs."""

    RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 0.5

    def __init__(
        self,
        max_retries: int = MAX_RETRIES,
        base_retry_delay: float = BASE_RETRY_DELAY,
    ) -> None:
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay

    def call(
        self,
        builder: PromptBuilder,
        max_output_tokens: int = 1024,
        tools: Optional[Any] = None,
    ) -> dict[str, Any]:
        url = builder.url
        headers = dict(builder.headers)
        payload = builder.to_api_payload(max_output_tokens=max_output_tokens, tools=tools)
        body = json.dumps(payload).encode("utf-8")

        ssl_context = ssl.create_default_context()
        attempts = 0

        while True:
            attempts += 1
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")

            try:
                with urllib.request.urlopen(req, timeout=60, context=ssl_context) as resp:
                    resp_data = resp.read().decode("utf-8")
                    return json.loads(resp_data)
            except urllib.error.HTTPError as e:
                status_code = e.code
                error_body = e.read().decode("utf-8", errors="replace")
                if status_code in self.RETRYABLE_STATUS_CODES and attempts <= self.max_retries:
                    time.sleep(self._retry_delay(attempts))
                    continue
                attempts_str = f"{attempts} attempt{'s' if attempts != 1 else ''}"
                raise ApiError(
                    f"API request failed after {attempts_str} ({status_code}): {error_body}"
                ) from e
            except TRANSIENT_EXCEPTIONS as e:
                if attempts > self.max_retries:
                    raise ApiError(
                        f"API request failed after {attempts} attempts: {type(e).__name__}: {e}"
                    ) from e
                time.sleep(self._retry_delay(attempts))
                continue

    def _retry_delay(self, attempt: int) -> float:
        return self.base_retry_delay * (2 ** (attempt - 1))
