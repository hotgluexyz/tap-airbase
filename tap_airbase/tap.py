"""Singer tap for Airbase."""

from __future__ import annotations

from typing import List

from hotglue_etl_exceptions import InvalidCredentialsError
from hotglue_singer_sdk import Tap, Stream
from hotglue_singer_sdk import typing as th
from hotglue_singer_sdk.helpers.capabilities import AlertingLevel

from tap_airbase.auth import AirbaseAuthenticator
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
            description=(
                "Earliest record date. Required when filter_by_entry_date is true; "
                "used as entry_date_start (through today) on the ledger_entries API."
            ),
        ),
        th.Property(
            "ledger_entry_status",
            th.StringType,
            description=(
                "Ledger entry status sent as the API status query parameter. Allowed values: sync_ready, sync_error, sync_complete"
                "If omitted, Airbase returns only sync_ready entries by default."
            ),
        ),
        th.Property(
            "filter_by_entry_date",
            th.BooleanType,
            description=(
                "When true, limits ledger_entries to entry_date_start (start_date) "
                "through entry_date_end (today)."
            ),
        ),
        th.Property(
            "ledger_entry_types",
            th.StringType,
            description=(
                "Comma-separated ledger entry type values. When set, only records "
                "whose type is in this list are emitted from ledger_entries."
            ),
        ),
    ).to_dict()

    @classmethod
    def access_token_support(cls, connector=None):
        return AirbaseAuthenticator, None

    def discover_streams(self) -> List[Stream]:
        return [
            LedgerEntriesStream(self),
            VendorsStream(self),
        ]


if __name__ == "__main__":
    TapAirbase.cli()
