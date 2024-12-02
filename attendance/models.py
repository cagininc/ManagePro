from django.db import models
from django.utils.timezone import now, make_aware
from datetime import datetime, time, timedelta
import pytz

class Attendance(models.Model):
    user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE)  # Personel bilgisi
    date = models.DateField(default=now)  # Giriş günü
    check_in = models.TimeField(null=True, blank=True)  # Ofise ilk giriş saati
    check_out = models.TimeField(null=True, blank=True)  # Ofisten son çıkış saati
    office_duration = models.DurationField(null=True, blank=True)  # Ofiste geçen toplam süre
    late_duration = models.DurationField(null=True, blank=True)  # Sabah 8:00'e göre geç kalma süresi

    def save(self, *args, **kwargs):
        # İstanbul saat dilimi tanımlaması
        istanbul_tz = pytz.timezone('Europe/Istanbul')

        # Sabah ofise giriş saati
        morning_start = time(8, 0)  # Sabah 08:00

        # Zaman dilimi ile ilgili işlemler
        if self.check_in:
            check_in_datetime = datetime.combine(self.date, self.check_in)
            check_in_datetime = make_aware(check_in_datetime, istanbul_tz)  # İstanbul saat dilimine göre ayarlama

            morning_start_datetime = datetime.combine(self.date, morning_start)
            morning_start_datetime = make_aware(morning_start_datetime, istanbul_tz)  # İstanbul saat dilimine göre ayarlama

            # Ofise geç kalma süresi
            if check_in_datetime > morning_start_datetime:
                self.late_duration = check_in_datetime - morning_start_datetime
            else:
                self.late_duration = timedelta(0)

        # Ofiste geçen süreyi hesapla (ilk giriş ve son çıkış arasındaki süre)
        if self.check_in and self.check_out:
            check_in_datetime = datetime.combine(self.date, self.check_in)
            check_in_datetime = make_aware(check_in_datetime, istanbul_tz)

            check_out_datetime = datetime.combine(self.date, self.check_out)
            check_out_datetime = make_aware(check_out_datetime, istanbul_tz)

            duration = check_out_datetime - check_in_datetime
            # Sadece saat ve dakikayı tutmak için saniyeyi yuvarlama
            duration = timedelta(hours=duration.seconds // 3600, minutes=(duration.seconds // 60) % 60)
            self.office_duration = duration

        # Eğer check_in var ama check_out yoksa, çıkış saati otomatik olarak gece 00:00 olarak ayarlanır(not planned yet)
        # if self.check_in and not self.check_out:
        #     midnight = time(0, 0)  # Gece 00:00
        #     check_out_datetime = datetime.combine(self.date + timedelta(days=1), midnight)
        #     check_out_datetime = make_aware(check_out_datetime, istanbul_tz)
        #     self.check_out = check_out_datetime.time()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
