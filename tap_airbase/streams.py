"""Stream type classes for tap-airbase."""

from __future__ import annotations

from hotglue_singer_sdk import typing as th
from typing_extensions import override

from tap_airbase.client import AirbaseStream

SPEND_OWNER = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("email", th.StringType),
)

SUBSIDIARY = th.ObjectType(
    th.Property("erp_reference_id", th.StringType),
    th.Property("name", th.StringType),
)

VENDOR = th.ObjectType(
    th.Property("airbase_id", th.StringType),
    th.Property("name", th.StringType),
    th.Property("erp_reference_id", th.StringType),
    th.Property("created_in_airbase", th.BooleanType),
)

ACCOUNT = th.ObjectType(
    th.Property("erp_reference_id", th.StringType),
    th.Property("name", th.StringType),
)

CURRENCY = th.ObjectType(
    th.Property("erp_reference_id", th.StringType),
    th.Property("iso_code", th.StringType),
)

EXPENSE_LINE = th.ObjectType(
    th.Property("line_number", th.IntegerType),
    th.Property("receipt_link", th.StringType),
    th.Property("account", ACCOUNT),
    th.Property("amount", th.StringType),
    th.Property("tags", th.ArrayType(th.CustomType({}))),
    th.Property("description", th.StringType),
)

SUBSIDIARY_REFERENCE = th.ObjectType(
    th.Property("airbase_id", th.StringType),
    th.Property("erp_reference_id", th.StringType),
)

AMOUNT = th.ObjectType(
    th.Property("amount", th.StringType),
    th.Property("currency", CURRENCY),
)


class LedgerEntriesStream(AirbaseStream):
    """Airbase accounting ledger entries."""

    name = "ledger_entries"
    path = "/v1/accounting/ledger_entries/"
    primary_keys = ["airbase_id"]
    schema = th.PropertiesList(
        th.Property("airbase_id", th.StringType),
        th.Property("erp_reference_id", th.StringType),
        th.Property("erp_url", th.StringType),
        th.Property("airbase_url", th.StringType),
        th.Property("type", th.StringType),
        th.Property("status", th.StringType),
        th.Property("error_message", th.StringType),
        th.Property("spend_owner", SPEND_OWNER),
        th.Property("subsidiary", SUBSIDIARY),
        th.Property("credit_mode", th.StringType),
        th.Property("vendor", VENDOR),
        th.Property("employee", th.ObjectType()),
        th.Property("invoice_number", th.StringType),
        th.Property("bank_account", th.ObjectType()),
        th.Property("ap_account", ACCOUNT),
        th.Property("applied_to", th.ObjectType()),
        th.Property("receipt_link", th.StringType),
        th.Property("entry_date", th.DateTimeType),
        th.Property("payment_entry_date", th.DateTimeType),
        th.Property("currency", CURRENCY),
        th.Property("total_amount", th.StringType),
        th.Property("transaction_tags", th.ArrayType(th.CustomType({}))),
        th.Property("notes", th.StringType),
        th.Property("is_amortized", th.BooleanType),
        th.Property("amortization_account", th.ObjectType()),
        th.Property("amortization_start_date", th.DateTimeType),
        th.Property("amortization_end_date", th.DateTimeType),
        th.Property("expense_list", th.ArrayType(EXPENSE_LINE)),
        th.Property("amounts", th.ObjectType(
            th.Property("amount", AMOUNT),
            th.Property("transaction_amount", AMOUNT),
            th.Property("settlement_amount", AMOUNT),
            th.Property("subsidiary_amount", AMOUNT),
        )),
    ).to_dict()


class VendorsStream(AirbaseStream):
    """Airbase accounting vendors."""

    name = "vendors"
    path = "/v1/accounting/vendors/"
    primary_keys = ["airbase_id"]
    schema = th.PropertiesList(
        th.Property("airbase_id", th.StringType),
        th.Property("erp_reference_id", th.StringType),
        th.Property("erp_parent_reference_id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("is_active", th.BooleanType),
        th.Property("email", th.StringType),
        th.Property(
            "subsidiary_reference_ids",
            th.ArrayType(SUBSIDIARY_REFERENCE),
        ),
    ).to_dict()

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token,
    ) -> dict:
        params = super().get_url_params(context, next_page_token)
        params["erp_reference_id"] = ""
        return params
