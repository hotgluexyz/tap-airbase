"""Authentication helpers for the Hotglue access-token flow."""

import json

from hotglue_singer_sdk.authenticators import OAuthAuthenticator


class AirbaseAuthenticator(OAuthAuthenticator):
    """Expose Airbase's static API key as an access token."""

    _config_file: str

    def update_access_token_locally(self) -> None:
        self._tap._config["access_token"] = self._tap._config["api_key"]
        with open(self._config_file, "w") as config_file:
            json.dump(self._tap._config, config_file, indent=4)
