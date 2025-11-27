"""
M-Pesa integration service for STK Push payments.

Uses Safaricom Daraja API for M-Pesa transactions.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import base64
import logging
from datetime import datetime
from typing import Any

from django.conf import settings

import requests

logger = logging.getLogger(__name__)


class MpesaConfig:
    """M-Pesa configuration from settings."""

    def __init__(self):
        self.consumer_key = getattr(settings, "MPESA_CONSUMER_KEY", "")
        self.consumer_secret = getattr(settings, "MPESA_CONSUMER_SECRET", "")
        self.shortcode = getattr(settings, "MPESA_SHORTCODE", "174379")  # Sandbox default
        self.passkey = getattr(settings, "MPESA_PASSKEY", "")
        self.callback_url = getattr(settings, "MPESA_CALLBACK_URL", "")
        self.environment = getattr(settings, "MPESA_ENVIRONMENT", "sandbox")

        # API URLs
        if self.environment == "production":
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"

        self.oauth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        self.stk_query_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"


class MpesaService:
    """
    M-Pesa payment service for STK Push.

    Handles OAuth authentication, STK Push initiation, and transaction queries.
    """

    def __init__(self):
        self.config = MpesaConfig()
        self._access_token = None
        self._token_expires = None

    def _get_access_token(self) -> str:
        """
        Get OAuth access token from Safaricom API.

        Returns:
            Access token string
        """
        # Check if we have a valid cached token
        if self._access_token and self._token_expires and datetime.now() < self._token_expires:
            return self._access_token

        try:
            # Create Basic Auth header
            credentials = f"{self.config.consumer_key}:{self.config.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json",
            }

            response = requests.get(self.config.oauth_url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            self._access_token = data["access_token"]

            # Token expires in 3599 seconds, we'll refresh earlier
            from datetime import timedelta

            self._token_expires = datetime.now() + timedelta(seconds=3500)

            logger.info("M-Pesa OAuth token obtained successfully")
            return self._access_token

        except requests.RequestException as e:
            logger.error(f"Failed to get M-Pesa access token: {e}")
            raise MpesaError(f"Failed to authenticate with M-Pesa: {e}")

    def _generate_password(self) -> tuple[str, str]:
        """
        Generate password for STK Push.

        Returns:
            Tuple of (password, timestamp)
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = f"{self.config.shortcode}{self.config.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        return password, timestamp

    def initiate_stk_push(
        self,
        phone_number: str,
        amount: int,
        account_reference: str,
        transaction_desc: str = "Hospital Payment",
    ) -> dict[str, Any]:
        """
        Initiate STK Push to customer's phone.

        Args:
            phone_number: Customer phone number (254XXXXXXXXX format)
            amount: Amount in KES (integer)
            account_reference: Reference for the transaction (e.g., invoice number)
            transaction_desc: Description of the transaction

        Returns:
            Dict with MerchantRequestID, CheckoutRequestID, ResponseCode, etc.
        """
        access_token = self._get_access_token()
        password, timestamp = self._generate_password()

        # Format phone number (ensure 254 prefix)
        phone = self._format_phone_number(phone_number)

        payload = {
            "BusinessShortCode": self.config.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.config.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.config.callback_url,
            "AccountReference": account_reference[:12],  # Max 12 chars
            "TransactionDesc": transaction_desc[:13],  # Max 13 chars
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            logger.info(f"Initiating STK Push for {phone}, amount: {amount}")

            response = requests.post(
                self.config.stk_push_url,
                json=payload,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"STK Push initiated: {data}")

            return {
                "success": data.get("ResponseCode") == "0",
                "merchant_request_id": data.get("MerchantRequestID"),
                "checkout_request_id": data.get("CheckoutRequestID"),
                "response_code": data.get("ResponseCode"),
                "response_description": data.get("ResponseDescription"),
                "customer_message": data.get("CustomerMessage"),
            }

        except requests.RequestException as e:
            logger.error(f"STK Push failed: {e}")
            raise MpesaError(f"Failed to initiate STK Push: {e}")

    def query_stk_status(self, checkout_request_id: str) -> dict[str, Any]:
        """
        Query the status of an STK Push transaction.

        Args:
            checkout_request_id: The CheckoutRequestID from STK Push response

        Returns:
            Dict with transaction status
        """
        access_token = self._get_access_token()
        password, timestamp = self._generate_password()

        payload = {
            "BusinessShortCode": self.config.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.config.stk_query_url,
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"STK Query result: {data}")

            return {
                "success": data.get("ResultCode") == "0",
                "result_code": data.get("ResultCode"),
                "result_desc": data.get("ResultDesc"),
                "response_code": data.get("ResponseCode"),
                "response_description": data.get("ResponseDescription"),
            }

        except requests.RequestException as e:
            logger.error(f"STK Query failed: {e}")
            raise MpesaError(f"Failed to query STK status: {e}")

    def _format_phone_number(self, phone: str) -> str:
        """
        Format phone number to 254XXXXXXXXX format.

        Args:
            phone: Phone number in various formats

        Returns:
            Formatted phone number
        """
        # Remove any non-digit characters
        phone = "".join(filter(str.isdigit, phone))

        # Handle different formats
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("+254"):
            phone = phone[1:]
        elif not phone.startswith("254"):
            phone = "254" + phone

        return phone

    @staticmethod
    def parse_callback(callback_data: dict) -> dict[str, Any]:
        """
        Parse M-Pesa callback data.

        Args:
            callback_data: Raw callback JSON from M-Pesa

        Returns:
            Parsed callback data with transaction details
        """
        try:
            body = callback_data.get("Body", {}).get("stkCallback", {})

            result = {
                "merchant_request_id": body.get("MerchantRequestID"),
                "checkout_request_id": body.get("CheckoutRequestID"),
                "result_code": str(body.get("ResultCode", "")),
                "result_desc": body.get("ResultDesc", ""),
                "success": body.get("ResultCode") == 0,
            }

            # Parse callback metadata if successful
            if result["success"] and "CallbackMetadata" in body:
                metadata = body["CallbackMetadata"].get("Item", [])
                for item in metadata:
                    name = item.get("Name", "")
                    value = item.get("Value")

                    if name == "Amount":
                        result["amount"] = value
                    elif name == "MpesaReceiptNumber":
                        result["receipt_number"] = value
                    elif name == "TransactionDate":
                        # Parse datetime from format like 20240115123456
                        result["transaction_date"] = datetime.strptime(str(value), "%Y%m%d%H%M%S")
                    elif name == "PhoneNumber":
                        result["phone_number"] = str(value)

            return result

        except Exception as e:
            logger.error(f"Failed to parse M-Pesa callback: {e}")
            return {
                "success": False,
                "result_code": "-1",
                "result_desc": f"Failed to parse callback: {e}",
            }


class MpesaError(Exception):
    """Exception for M-Pesa related errors."""

    pass


# Result codes reference
MPESA_RESULT_CODES = {
    "0": "Success",
    "1": "Insufficient Balance",
    "1032": "Request Cancelled by User",
    "1037": "Timeout in completing transaction",
    "2001": "Wrong PIN",
    "17": "Internal error",
}
