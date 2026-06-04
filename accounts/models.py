"""
Accounts Models - Custom User Model for SACCO System
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Extended User model with SACCO-specific fields."""

    ROLE_MEMBER = 'member'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_MEMBER, 'Member'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    member_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.member_number or 'N/A'})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_staff

    @property
    def is_member(self):
        return self.role == self.ROLE_MEMBER

    def save(self, *args, **kwargs):
        # Auto-generate member number
        if not self.member_number:
            super().save(*args, **kwargs)
            self.member_number = f"SACCO-{self.pk:05d}"
            User.objects.filter(pk=self.pk).update(member_number=self.member_number)
        else:
            super().save(*args, **kwargs)
