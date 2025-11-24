"""
Common model mixins and abstract base classes.
"""

from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Add created_at and updated_at timestamps to models."""
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Add soft delete functionality to models."""
    
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(using=using)
    
    def hard_delete(self):
        """Permanently delete the object."""
        super().delete()
    
    def restore(self):
        """Restore a soft-deleted object."""
        self.deleted_at = None
        self.is_deleted = False
        self.save()


class AuditMixin(TimestampMixin):
    """
    Add audit fields to models.
    Requires created_by and updated_by ForeignKey fields to User model.
    """
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Override save to capture user context if available."""
        # User context should be set by middleware or manually
        # This is a placeholder - actual implementation in views
        super().save(*args, **kwargs)
