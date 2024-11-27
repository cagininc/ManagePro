from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class Leave(models.Model):
    user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE)  # İzin alan kullanıcı
    start_date = models.DateField()  # İzin başlangıç tarihi
    end_date = models.DateField()  # İzin bitiş tarihi
    created_at = models.DateTimeField(auto_now_add=True)  # İzin talep tarihi
    status_choices = [
        ('approved', 'Onaylandı'),
        ('pending', 'Beklemede'),
        ('rejected', 'Reddedildi'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    reason = models.TextField(null=True, blank=True)  # İzin nedeni

    def leave_duration(self):
        """
        İzin süresini (gün olarak) hesaplar.
        """
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.user.username} - {self.start_date} - {self.end_date}"
