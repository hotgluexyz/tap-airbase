"""Stream type classes for tap-airbase."""

from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime
from urllib.parse import unquote, urlparse

import requests
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
    th.Property("amortization_start_date", th.DateTimeType),
    th.Property("amortization_end_date", th.DateTimeType),
)

SUBSIDIARY_REFERENCE = th.ObjectType(
    th.Property("airbase_id", th.StringType),
    th.Property("erp_reference_id", th.StringType),
)

AMOUNT = th.ObjectType(
    th.Property("amount", th.StringType),
    th.Property("currency", CURRENCY),
)

# Same attachment shape as tap-airwallex. Rillet accepts these types on
# bills, charges, and reimbursements.
_EXTENSION_CONTENT_TYPES = {
    "pdf": "application/pdf",
    "txt": "text/plain",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "csv": "text/csv",
    "rtf": "application/rtf",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "bmp": "image/bmp",
    "pages": "application/vnd.apple.pages",
    "numbers": "application/vnd.apple.numbers",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "ppt": "application/vnd.ms-powerpoint",
}

ATTACHMENT = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("file_name", th.StringType),
    th.Property("file_url", th.StringType),
    th.Property("content_type", th.StringType),
    th.Property("attachment_path", th.StringType),
)


def receipt_attachments(row: dict) -> list[dict]:
    """Collect header and line receipt links into Airwallex-style attachments."""
    urls: list[str] = []
    header_url = row.get("receipt_link")
    if header_url:
        urls.append(header_url)
    for line in row.get("expense_list") or []:
        line_url = (line or {}).get("receipt_link")
        if line_url and line_url not in urls:
            urls.append(line_url)

    attachments = []
    record_id = row.get("airbase_id") or "receipt"
    for index, url in enumerate(urls):
        path = unquote(urlparse(url).path)
        file_name = path.rsplit("/", 1)[-1] or f"{record_id}_{index}"
        extension = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        attachments.append(
            {
                "id": f"{record_id}_{index}",
                "file_name": file_name,
                "file_url": url,
                "content_type": _EXTENSION_CONTENT_TYPES.get(extension),
            }
        )
    return attachments


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
        th.Property("posting_date", th.DateTimeType),
        th.Property("applied_to", th.ObjectType()),
        th.Property("receipt_link", th.StringType),
        th.Property("attachments", th.ArrayType(ATTACHMENT)),
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

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token,
    ) -> dict:
        """
        Return URL parameters for the ledger_entries endpoint.

        Adds a 'status' parameter to the URL params if 'ledger_entry_status'
        is set in the configuration. Without the param Airbase syncs by default only 'sync_ready' entries.
        """
        params = super().get_url_params(context, next_page_token)
        if self.config.get("ledger_entry_status"):
            params["status"] = self.config.get("ledger_entry_status")
        if self.config.get("filter_by_entry_date"):
            start_date_raw = self.config.get("start_date")
            if start_date_raw:
                start_date = datetime.fromisoformat(start_date_raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            else:
                raise ValueError("start_date is required for filtering by entry date")
            end_date = datetime.now().strftime("%Y-%m-%d")
            params["entry_date_start"] = start_date
            params["entry_date_end"] = end_date

        return params

    @override
    def post_process(self, row: dict, context: dict | None) -> dict:
        """
        If 'ledger_entry_types' is set in the configuration, only return rows whose
        'type' field is present in the provided ledger_entry_types (comma-separated).
        Otherwise, return the row as-is.

        Receipt links on the entry and its expense lines are copied to attachments
        so bills, charges, and reimbursements can upload the same file types.

        Args:
            row (dict): The row (record) to post-process.
            context (dict | None): The stream context.

        Returns:
            dict: The processed row, or None if the type is not accepted.
        """
        row = super().post_process(row, context)
        if not row:
            return row

        ledger_entry_types = self.config.get("ledger_entry_types")
        if ledger_entry_types:
            allowed_types = [
                ledger_entry_type.strip()
                for ledger_entry_type in ledger_entry_types.split(",")
            ]
            if row.get("type") not in allowed_types:
                return None

        row["attachments"] = receipt_attachments(row)
        if self.config.get("download_attachments", True):
            record_id = row.get("erp_reference_id") or row.get("airbase_id") or "unknown"
            for attachment in row["attachments"]:
                attachment["attachment_path"] = self._download_attachment(
                    attachment, record_id
                )
        return row

    def _download_attachment(self, attachment: dict, record_id: str) -> str | None:
        """Download a receipt and return its path relative to sync-output."""
        url = attachment.get("file_url")
        if not url:
            return None

        file_name = attachment.get("file_name") or "attachment"
        file_name = os.path.basename(file_name.strip())
        file_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", file_name) or "attachment"
        if attachment.get("id") is not None:
            file_name = f"{attachment['id']}_{file_name}"

        sync_output = self.get_sync_output_folder()
        attachments_root = os.path.realpath(os.path.join(sync_output, "attachments"))
        relative_path = os.path.join("attachments", str(record_id), file_name)
        target_path = os.path.realpath(os.path.join(sync_output, relative_path))
        try:
            contained = os.path.commonpath([attachments_root, target_path]) == attachments_root
        except ValueError:
            contained = False
        if not contained or target_path == attachments_root:
            self.logger.warning(
                "Skipping attachment %s: destination %s is outside %s",
                attachment.get("id"),
                target_path,
                attachments_root,
            )
            return None
        temp_path = None
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with requests.get(url, stream=True, timeout=60) as response:
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(
                    mode="wb", dir=os.path.dirname(target_path), delete=False
                ) as handle:
                    temp_path = handle.name
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)
            os.replace(temp_path, target_path)
            temp_path = None
            self.logger.info("Downloaded attachment to %s", target_path)
            return relative_path
        except Exception as ex:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            logged_url = urlparse(url)._replace(query="", fragment="").geturl()
            self.logger.warning(
                "Failed to download attachment %s from %s: %s",
                attachment.get("id"),
                logged_url,
                ex,
            )
            return None


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
