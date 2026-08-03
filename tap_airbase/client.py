"""HTTP API client for Airbase streams."""

from __future__ import annotations

from typing import Any

import requests
from hotglue_singer_sdk.authenticators import APIKeyAuthenticator
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override


class AirbaseStream(RESTStream):
    """Base Airbase API stream."""

    records_jsonpath = "$.data[*]"
    replication_key = None

    @override
    @property
    def url_base(self) -> str:
        if self.config.get("sandbox"):
            return "https://api-stage.airbase.io"
        return "https://api.airbase.io"

    @override
    @property
    def authenticator(self) -> APIKeyAuthenticator:
        return APIKeyAuthenticator(
            stream=self,
            key="Authorization",
            value=f"Token {self.config['api_key']}",
            location="header",
        )

    @override
    @property
    def http_headers(self) -> dict[str, str]:
        return {"Accept": "application/json"}

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        page = previous_token or 1
        if next(iter(self.parse_response(response)), None):
            self.logger.info(f"Next page token: {page + 1}")
            return page + 1
        return None

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if next_page_token:
            params["page"] = next_page_token
        return params
