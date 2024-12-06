# notifications/models.py
from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('late', 'Geç Kalma'),
        ('leave_request', 'İzin Talebi'),
        ('leave_approval', 'İzin Onayı'),
        # İleride başka tipler de ekleyebiliriz.
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Bildirimin gönderildiği kullanıcı
    message = models.TextField()  # Bildirim içeriği
    created_at = models.DateTimeField(auto_now_add=True)  # Bildirimin oluşturulma tarihi
    is_read = models.BooleanField(default=False)  # Okunup okunmadığını belirtir
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)  # Bildirim türü

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.message[:20]}"
