"""Singer tap for Airbase."""

from __future__ import annotations

from typing import List

from hotglue_etl_exceptions import InvalidCredentialsError
from hotglue_singer_sdk import Tap, Stream
from hotglue_singer_sdk import typing as th
from hotglue_singer_sdk.helpers.capabilities import AlertingLevel

from tap_airbase.streams import LedgerEntriesStream, VendorsStream


class TapAirbase(Tap):
    """Airbase tap."""

    name = "tap-airbase"

    alerting_level = AlertingLevel.ERROR
    exception_alerting_level_map = {
        InvalidCredentialsError: AlertingLevel.NONE,
    }

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="Airbase API key (sent as Authorization: Token …)",
        ),
        th.Property(
            "sandbox",
            th.BooleanType,
            description="Use the Airbase staging API (api-stage.airbase.io)",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest record date (reserved for future incremental sync)",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        return [
            LedgerEntriesStream(self),
            VendorsStream(self),
        ]


if __name__ == "__main__":
    TapAirbase.cli()
