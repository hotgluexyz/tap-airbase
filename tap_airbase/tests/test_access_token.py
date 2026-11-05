"""Tests Airbase access-token support."""

import json

from tap_airbase.tap import TapAirbase


def test_access_token_support_copies_api_key(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"api_key": "airbase-api-key"}))
    tap = TapAirbase(config=config_path)

    assert TapAirbase.fetch_access_token(tap) == {
        "access_token": "airbase-api-key"
    }
    assert json.loads(config_path.read_text())["access_token"] == "airbase-api-key"
