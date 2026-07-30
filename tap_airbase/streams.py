"""Stream type classes for tap-airbase."""

from __future__ import annotations

from typing_extensions import override

from tap_airbase.client import AirbaseStream


class LedgerEntriesStream(AirbaseStream):
    """Airbase accounting ledger entries."""

    name = "ledger_entries"
    path = "/v1/accounting/ledger_entries/"
    primary_keys = ["airbase_id"]
    schema = {
        "type": "object",
        "properties": {
            "airbase_id": {"type": ["string", "null"]},
            "erp_reference_id": {"type": ["string", "null"]},
            "erp_url": {"type": ["string", "null"]},
            "airbase_url": {"type": ["string", "null"]},
            "type": {"type": ["string", "null"]},
            "status": {"type": ["string", "null"]},
            "error_message": {"type": ["string", "null"]},
            "spend_owner": {
                "type": ["object", "null"],
                "properties": {
                    "name": {"type": ["string", "null"]},
                    "email": {"type": ["string", "null"]},
                },
                "additionalProperties": True,
            },
            "subsidiary": {
                "type": ["object", "null"],
                "properties": {
                    "erp_reference_id": {"type": ["string", "null"]},
                    "name": {"type": ["string", "null"]},
                },
                "additionalProperties": True,
            },
            "credit_mode": {"type": ["string", "null"]},
            "vendor": {
                "type": ["object", "null"],
                "properties": {
                    "airbase_id": {"type": ["string", "null"]},
                    "name": {"type": ["string", "null"]},
                    "erp_reference_id": {"type": ["string", "null"]},
                    "created_in_airbase": {"type": ["boolean", "null"]},
                },
                "additionalProperties": True,
            },
            "employee": {"type": ["object", "null"]},
            "invoice_number": {"type": ["string", "null"]},
            "bank_account": {"type": ["object", "null"]},
            "ap_account": {
                "type": ["object", "null"],
                "properties": {
                    "erp_reference_id": {"type": ["string", "null"]},
                    "name": {"type": ["string", "null"]},
                },
                "additionalProperties": True,
            },
            "applied_to": {"type": ["object", "null"]},
            "receipt_link": {"type": ["string", "null"]},
            "entry_date": {"type": ["string", "null"], "format": "date-time"},
            "payment_entry_date": {"type": ["string", "null"], "format": "date-time"},
            "currency": {
                "type": ["object", "null"],
                "properties": {
                    "erp_reference_id": {"type": ["string", "null"]},
                    "iso_code": {"type": ["string", "null"]},
                },
                "additionalProperties": True,
            },
            "total_amount": {"type": ["string", "null"]},
            "transaction_tags": {"type": ["array", "null"], "items": {}},
            "notes": {"type": ["string", "null"]},
            "is_amortized": {"type": ["boolean", "null"]},
            "amortization_account": {"type": ["object", "null"]},
            "amortization_start_date": {"type": ["string", "null"], "format": "date-time"},
            "amortization_end_date": {"type": ["string", "null"], "format": "date-time"},
            "expense_list": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "line_number": {"type": ["integer", "null"]},
                        "receipt_link": {"type": ["string", "null"]},
                        "account": {
                            "type": ["object", "null"],
                            "properties": {
                                "erp_reference_id": {"type": ["string", "null"]},
                                "name": {"type": ["string", "null"]},
                            },
                            "additionalProperties": True,
                        },
                        "amount": {"type": ["string", "null"]},
                        "tags": {"type": ["array", "null"], "items": {}},
                        "description": {"type": ["string", "null"]},
                    },
                    "additionalProperties": True,
                },
            },
        },
        "additionalProperties": True,
    }


class VendorsStream(AirbaseStream):
    """Airbase accounting vendors."""

    name = "vendors"
    path = "/v1/accounting/vendors/"
    primary_keys = ["airbase_id"]
    schema = {
        "type": "object",
        "properties": {
            "airbase_id": {"type": ["string", "null"]},
            "erp_reference_id": {"type": ["string", "null"]},
            "erp_parent_reference_id": {"type": ["string", "null"]},
            "name": {"type": ["string", "null"]},
            "is_active": {"type": ["boolean", "null"]},
            "email": {"type": ["string", "null"]},
            "subsidiary_reference_ids": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "airbase_id": {"type": ["string", "null"]},
                        "erp_reference_id": {"type": ["string", "null"]},
                    },
                },
            },
        },
    }

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token,
    ) -> dict:
        params = super().get_url_params(context, next_page_token)
        params["erp_reference_id"] = ""
        return params
