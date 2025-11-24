"""Hospital Native C Extensions - Python wrappers"""

__version__ = "0.1.0"

try:
    from . import _cutils, _hl7val
    
    # Re-export for convenience
    aes_gcm_encrypt = _cutils.aes_gcm_encrypt
    aes_gcm_decrypt = _cutils.aes_gcm_decrypt
    sha256 = _cutils.sha256
    generate_token = _cutils.generate_token
    hex_encode = _cutils.hex_encode
    
    validate_hl7_segment = _hl7val.validate_segment
    extract_hl7_field = _hl7val.extract_field
    
    # Note: _authz and _bill C extensions to be added in future
    # For now, use the Django wrapper functions in apps.core.utils
    
except ImportError as e:
    # Fallback message if C extensions not built
    import warnings
    warnings.warn(f"C extensions not available: {e}. Some features will be limited.")
