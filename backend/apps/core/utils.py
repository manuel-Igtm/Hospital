"""
Wrappers for C module functionality with graceful fallbacks.

Provides Python wrappers around C extensions with fallback to pure Python
when C modules are not available or disabled.
"""

import hashlib
import logging
import secrets
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import C modules
C_MODULES_AVAILABLE = False
hospital_native = None  # type: ignore[assignment]
try:
    if settings.HOSPITAL_SETTINGS.get("ENABLE_C_MODULES", False):
        import hospital_native  # type: ignore[import-not-found,no-redef]

        C_MODULES_AVAILABLE = True
        logger.info("✓ C modules loaded successfully")
except ImportError as e:
    logger.warning(f"C modules not available, using Python fallbacks: {e}")


# Cryptographic utilities


def generate_pii_token() -> str:
    """
    Generate a secure random token for PII pseudonymization.

    Returns:
        Hex-encoded 32-byte token
    """
    if C_MODULES_AVAILABLE:
        try:
            token_bytes = hospital_native.generate_token()
            return hospital_native.hex_encode(token_bytes)
        except Exception as e:
            logger.warning(f"C token generation failed, using Python: {e}")

    # Python fallback
    return secrets.token_hex(32)


def sha256_hash(data: bytes) -> str:
    """
    Compute SHA-256 hash of data.

    Args:
        data: Bytes to hash

    Returns:
        Hex-encoded hash
    """
    if C_MODULES_AVAILABLE:
        try:
            hash_bytes = hospital_native.sha256(data)
            return hospital_native.hex_encode(hash_bytes)
        except Exception as e:
            logger.warning(f"C SHA-256 failed, using Python: {e}")

    # Python fallback
    return hashlib.sha256(data).hexdigest()


def aes_gcm_encrypt(plaintext: bytes, key: bytes) -> bytes:
    """
    Encrypt data using AES-256-GCM.

    Args:
        plaintext: Data to encrypt
        key: 32-byte encryption key

    Returns:
        Encrypted data (IV + ciphertext + tag)
    """
    if C_MODULES_AVAILABLE:
        try:
            return hospital_native.aes_gcm_encrypt(plaintext, key)
        except Exception as e:
            logger.error(f"C encryption failed: {e}")
            raise

    # Python fallback using cryptography library
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext


def aes_gcm_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """
    Decrypt data using AES-256-GCM.

    Args:
        ciphertext: Encrypted data (IV + ciphertext + tag)
        key: 32-byte decryption key

    Returns:
        Decrypted plaintext
    """
    if C_MODULES_AVAILABLE:
        try:
            return hospital_native.aes_gcm_decrypt(ciphertext, key)
        except Exception as e:
            logger.error(f"C decryption failed: {e}")
            raise

    # Python fallback using cryptography library
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    aesgcm = AESGCM(key)
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    return aesgcm.decrypt(nonce, ct, None)


# HL7 validation


def validate_hl7_segment(segment: str) -> bool:
    """
    Validate HL7 v2 segment structure.

    Args:
        segment: HL7 segment string

    Returns:
        True if valid

    Raises:
        ValueError: If segment is invalid
    """
    if C_MODULES_AVAILABLE:
        try:
            hospital_native.validate_hl7_segment(segment)
            return True
        except Exception as e:
            logger.warning(f"C HL7 validation failed, using Python: {e}")

    # Python fallback - basic validation
    if not segment or len(segment) < 4:
        raise ValueError("Segment too short")

    if segment[3] != "|":
        raise ValueError("Invalid field delimiter")

    # Check segment ID (3 chars)
    seg_id = segment[:3]
    if not seg_id.isupper():
        raise ValueError("Invalid segment ID")

    return True
