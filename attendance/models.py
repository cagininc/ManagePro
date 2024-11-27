from django.db import models
from django.utils.timezone import now
from datetime import datetime, time, timedelta

class Attendance(models.Model):
    user = models.ForeignKey('user.CustomUser', on_delete=models.CASCADE)  # Personel bilgisi
    date = models.DateField(default=now)  # Giriş günü
    check_in = models.TimeField(null=True, blank=True)  # Ofise ilk giriş saati
    check_out = models.TimeField(null=True, blank=True)  # Ofisten son çıkış saati
    office_duration = models.DurationField(null=True, blank=True)  # Ofiste geçen toplam süre
    late_duration = models.DurationField(null=True, blank=True)  # Sabah 8:00'e göre geç kalma süresi

    def save(self, *args, **kwargs):
        # Sabah ofise giriş saati
        morning_start = time(8, 0)  # Sabah 08:00
        
        # Ofise geç kalma süresi
        if self.check_in:
            check_in_datetime = datetime.combine(self.date, self.check_in)
            morning_start_datetime = datetime.combine(self.date, morning_start)
            
            if check_in_datetime > morning_start_datetime:
                self.late_duration = check_in_datetime - morning_start_datetime
            else:
                self.late_duration = timedelta(0)

        # Ofiste geçen süreyi hesapla (ilk giriş ve son çıkış arasındaki süre)
        if self.check_in and self.check_out:
            check_in_datetime = datetime.combine(self.date, self.check_in)
            check_out_datetime = datetime.combine(self.date, self.check_out)
            self.office_duration = check_out_datetime - check_in_datetime
        
   
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
