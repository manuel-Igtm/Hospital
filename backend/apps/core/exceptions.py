"""
Custom exception handlers for DRF.

Provides RFC 7807 Problem Details for HTTP APIs compliance.
"""

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns RFC 7807 Problem Details format.

    Returns:
        Response with structure:
        {
            "type": "about:blank",
            "title": "Error Title",
            "status": 400,
            "detail": "Detailed error message",
            "instance": "/api/v1/resource/123",
            "errors": {...}  // Optional field-specific errors
        }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize error response format
        error_data = {
            "type": "about:blank",
            "title": exc.__class__.__name__.replace("_", " ").title(),
            "status": response.status_code,
            "detail": str(exc),
            "instance": context["request"].path,
        }

        # Add field-specific errors if available
        if hasattr(exc, "detail") and isinstance(exc.detail, dict):
            error_data["errors"] = exc.detail
        elif hasattr(exc, "detail") and isinstance(exc.detail, list):
            error_data["errors"] = {"non_field_errors": exc.detail}

        response.data = error_data

        # Log server errors
        if response.status_code >= 500:
            logger.error(f"Server error: {exc}", exc_info=True, extra={"request": context["request"]})
    else:
        # Handle Django validation errors
        if isinstance(exc, DjangoValidationError):
            error_data = {
                "type": "about:blank",
                "title": "Validation Error",
                "status": status.HTTP_400_BAD_REQUEST,
                "detail": "Invalid data provided",
                "instance": context["request"].path,
                "errors": exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages},
            }
            response = Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        # Handle 404 errors
        elif isinstance(exc, Http404):
            error_data = {
                "type": "about:blank",
                "title": "Not Found",
                "status": status.HTTP_404_NOT_FOUND,
                "detail": str(exc) or "Resource not found",
                "instance": context["request"].path,
            }
            response = Response(error_data, status=status.HTTP_404_NOT_FOUND)

        # Log unhandled exceptions
        else:
            logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={"request": context["request"]})

    return response
