"""
Patient model with encrypted PII storage.

Uses libcutils C module for AES-256-GCM encryption of sensitive
fields like SSN.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import hashlib
import uuid
from datetime import date

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from apps.core.utils import aes_gcm_decrypt, aes_gcm_encrypt


class Gender(models.TextChoices):
    """Gender choices for patient records."""

    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"
    UNKNOWN = "U", "Unknown"


class BloodType(models.TextChoices):
    """Blood type choices."""

    A_POS = "A+", "A Positive"
    A_NEG = "A-", "A Negative"
    B_POS = "B+", "B Positive"
    B_NEG = "B-", "B Negative"
    AB_POS = "AB+", "AB Positive"
    AB_NEG = "AB-", "AB Negative"
    O_POS = "O+", "O Positive"
    O_NEG = "O-", "O Negative"
    UNKNOWN = "UNK", "Unknown"


def generate_mrn():
    """
    Generate a unique Medical Record Number.

    Format: MRN-YYYYMMDD-XXXX where XXXX is a random 4-digit number.
    """
    import random
    from datetime import datetime

    date_part = datetime.now().strftime("%Y%m%d")
    random_part = str(random.randint(1000, 9999))

    return f"MRN-{date_part}-{random_part}"


class Patient(models.Model):
    """
    Patient model with encrypted sensitive data.

    The SSN field is encrypted using AES-256-GCM via the libcutils C module.
    A hash of the SSN is stored for lookup purposes.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique identifier for the patient"
    )

    # Medical Record Number - unique identifier
    mrn = models.CharField(
        max_length=20, unique=True, default=generate_mrn, db_index=True, help_text="Medical Record Number"
    )

    # Personal Information
    first_name = models.CharField(max_length=100, help_text="Patient first name")
    last_name = models.CharField(max_length=100, help_text="Patient last name")
    middle_name = models.CharField(max_length=100, blank=True, help_text="Patient middle name")
    date_of_birth = models.DateField(help_text="Date of birth")
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.UNKNOWN, help_text="Patient gender")

    # Encrypted SSN (stored as binary)
    _ssn_encrypted = models.BinaryField(null=True, blank=True, help_text="Encrypted SSN (AES-256-GCM)")
    # Hash of SSN for lookup (SHA-256)
    ssn_hash = models.CharField(
        max_length=64, null=True, blank=True, db_index=True, help_text="SHA-256 hash of SSN for lookups"
    )

    # Contact Information
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(regex=r"^\+?1?\d{9,15}$", message="Phone number must be 9-15 digits")],
        help_text="Phone number",
    )
    email = models.EmailField(blank=True, help_text="Email address")

    # Address
    address_line1 = models.CharField(max_length=200, blank=True, help_text="Street address line 1")
    address_line2 = models.CharField(max_length=200, blank=True, help_text="Street address line 2")
    city = models.CharField(max_length=100, blank=True, help_text="City")
    state = models.CharField(max_length=50, blank=True, help_text="State/Province")
    postal_code = models.CharField(max_length=20, blank=True, help_text="ZIP/Postal code")
    country = models.CharField(max_length=50, default="USA", help_text="Country")

    # Medical Information
    blood_type = models.CharField(
        max_length=4, choices=BloodType.choices, default=BloodType.UNKNOWN, help_text="Blood type"
    )
    allergies = models.TextField(blank=True, help_text="Known allergies (comma-separated)")

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, help_text="Emergency contact name")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, help_text="Emergency contact phone")
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, help_text="Relationship to patient")

    # Status
    is_active = models.BooleanField(default=True, help_text="Whether patient record is active")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the patient was registered")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the patient record was last updated")

    class Meta:
        db_table = "patients"
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["date_of_birth"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.mrn})"

    @property
    def full_name(self):
        """Return patient's full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)

    @property
    def age(self):
        """Calculate patient's age."""
        today = date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def _get_encryption_key(self):
        """Get the PII encryption key from settings."""
        key = settings.HOSPITAL_SETTINGS.get("PII_ENCRYPTION_KEY")
        if not key:
            raise ValueError("PII_ENCRYPTION_KEY not configured")

        # Ensure key is 32 bytes for AES-256
        if isinstance(key, str):
            key = key.encode("utf-8")

        # Hash the key to ensure exactly 32 bytes
        return hashlib.sha256(key).digest()

    def set_ssn(self, ssn: str):
        """
        Encrypt and store SSN.

        Args:
            ssn: Plain text SSN (e.g., "123-45-6789")
        """
        if not ssn:
            self._ssn_encrypted = None
            self.ssn_hash = None
            return

        # Normalize SSN (remove dashes)
        ssn_normalized = ssn.replace("-", "").replace(" ", "")

        # Store hash for lookups
        self.ssn_hash = hashlib.sha256(ssn_normalized.encode()).hexdigest()

        # Encrypt the SSN
        key = self._get_encryption_key()
        self._ssn_encrypted = aes_gcm_encrypt(ssn_normalized.encode(), key)

    def get_ssn(self) -> str | None:
        """
        Decrypt and return SSN.

        Returns:
            Decrypted SSN or None if not set
        """
        if not self._ssn_encrypted:
            return None

        key = self._get_encryption_key()
        decrypted = aes_gcm_decrypt(bytes(self._ssn_encrypted), key)
        return decrypted.decode()

    @property
    def ssn_masked(self) -> str | None:
        """Return masked SSN (XXX-XX-1234)."""
        ssn = self.get_ssn()
        if not ssn:
            return None
        return f"XXX-XX-{ssn[-4:]}"

    @classmethod
    def find_by_ssn(cls, ssn: str):
        """
        Find patient by SSN (using hash lookup).

        Args:
            ssn: Plain text SSN

        Returns:
            Patient instance or None
        """
        ssn_normalized = ssn.replace("-", "").replace(" ", "")
        ssn_hash = hashlib.sha256(ssn_normalized.encode()).hexdigest()

        try:
            return cls.objects.get(ssn_hash=ssn_hash)
        except cls.DoesNotExist:
            return None
