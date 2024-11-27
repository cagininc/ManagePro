from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('personel', 'Personel'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='personel')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    annual_leave_days = models.IntegerField(default=15)  #  izin hakkı
    email = models.EmailField(unique=True)  # Benzersiz e-posta adresi
    remaining_leave_days = models.IntegerField(default=15)  # Yıllık izin hakkı

    def __str__(self):
        return self.username
