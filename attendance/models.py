from django.db import models
from django.utils import timezone
from datetime import datetime, time, timedelta

class Attendance(models.Model):
    user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE)  # Personel bilgisi
    date = models.DateField(default=timezone.now)  # Giriş günü
    check_in = models.TimeField(null=True, blank=True)  # Ofise ilk giriş saati
    check_out = models.TimeField(null=True, blank=True)  # Ofisten son çıkış saati
    office_duration = models.DurationField(null=True, blank=True)  # Ofiste geçen toplam süre
    late_duration = models.DurationField(null=True, blank=True)  # Sabah 8:00'e göre geç kalma süresi

    def save(self, *args, **kwargs):
        # Sabah ofise giriş saati (08:00)
        morning_start = time(8, 0)

        # check_in zamanı belirlenmişse işlemleri gerçekleştir
        if self.check_in:
            check_in_datetime = datetime.combine(self.date, self.check_in)
            check_in_datetime = timezone.make_aware(check_in_datetime, timezone.get_current_timezone())  # Saat dilimini uygun hale getir

            morning_start_datetime = datetime.combine(self.date, morning_start)
            morning_start_datetime = timezone.make_aware(morning_start_datetime, timezone.get_current_timezone())

            # Ofise geç kalma süresi
            if check_in_datetime > morning_start_datetime:
                self.late_duration = check_in_datetime - morning_start_datetime
            else:
                self.late_duration = timedelta(0)

        # Ofiste geçen süreyi hesapla (ilk giriş ve son çıkış arasındaki süre)
        if self.check_in and self.check_out:
            check_in_datetime = datetime.combine(self.date, self.check_in)
            check_in_datetime = timezone.make_aware(check_in_datetime, timezone.get_current_timezone())

            check_out_datetime = datetime.combine(self.date, self.check_out)
            check_out_datetime = timezone.make_aware(check_out_datetime, timezone.get_current_timezone())

            # Ofiste geçen süreyi hesapla
            duration = check_out_datetime - check_in_datetime
            # Sadece saat ve dakikayı tutmak için saniyeyi yuvarlama
            self.office_duration = timedelta(hours=duration.seconds // 3600, minutes=(duration.seconds // 60) % 60)

        # Eğer check_in var ama check_out yoksa, çıkış saati otomatik olarak akşam 18:00 olarak ayarlanır
        # if self.check_in and not self.check_out:
        #     evening_end = time(18, 0)  # Akşam 18:00
        #     check_out_datetime = datetime.combine(self.date, evening_end)
        #     check_out_datetime = timezone.make_aware(check_out_datetime, timezone.get_current_timezone())
        #     self.check_out = check_out_datetime.time()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
