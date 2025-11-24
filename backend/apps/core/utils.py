"""
Wrappers for C module functionality with graceful fallbacks.

Provides Python wrappers around C extensions with fallback to pure Python
when C modules are not available or disabled.
"""

from django.conf import settings
from typing import Optional
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)

# Try to import C modules
C_MODULES_AVAILABLE = False
try:
    if settings.HOSPITAL_SETTINGS.get('ENABLE_C_MODULES', False):
        import hospital_native
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
    
    if segment[3] != '|':
        raise ValueError("Invalid field delimiter")
    
    # Check segment ID (3 chars)
    seg_id = segment[:3]
    if not seg_id.isupper():
        raise ValueError("Invalid segment ID")
    
    return True


# Authorization helpers

def evaluate_abac_policy(context: dict, policy: str) -> bool:
    """
    Evaluate ABAC policy expression.
    
    Args:
        context: Dictionary of attributes (role, department, level, etc.)
        policy: Policy expression string
        
    Returns:
        True if policy allows, False if denies
    """
    if C_MODULES_AVAILABLE:
        try:
            # TODO: Implement full C ABAC evaluation
            pass
        except Exception as e:
            logger.warning(f"C ABAC evaluation failed, using Python: {e}")
    
    # Python fallback - simple expression evaluation
    # WARNING: This is simplified. Production would use a proper policy engine.
    for key, value in context.items():
        policy = policy.replace(key, repr(value))
    
    try:
        return eval(policy, {"__builtins__": {}})
    except Exception:
        return False


# Billing helpers

def calculate_invoice(codes: list[str], quantities: list[int]) -> dict:
    """
    Calculate invoice totals from billing codes.
    
    Args:
        codes: List of ICD/DRG/CPT codes
        quantities: List of quantities for each code
        
    Returns:
        Dictionary with subtotal, tax, total (in cents)
    """
    if C_MODULES_AVAILABLE:
        try:
            # TODO: Implement C billing calculation
            pass
        except Exception as e:
            logger.warning(f"C billing calculation failed, using Python: {e}")
    
    # Python fallback - simplified calculation
    # In production, load from database or config
    default_prices = {
        'I21.0': 150000,  # $1,500
        'I10': 50000,     # $500
        '99213': 12000,   # $120
        '99214': 18000,   # $180
    }
    
    subtotal = 0
    for code, qty in zip(codes, quantities):
        price = default_prices.get(code, 10000)  # $100 default
        subtotal += price * qty
    
    tax = 0  # No tax on medical services typically
    total = subtotal + tax
    
    return {
        'subtotal_cents': subtotal,
        'tax_cents': tax,
        'total_cents': total,
    }
