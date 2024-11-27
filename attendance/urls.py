from django.urls import path
from .views import check_in, check_out,user_attendance_list,check_status,user_attendance_weekly,server_side_attendance

urlpatterns = [
    
    path('', user_attendance_list, name='attendance_list'),  # GET
    path('check_in/', check_in, name='check_in'),  # Ofise giriş POST
    path('check_out/', check_out, name='check_out'),  # Ofisten çıkış  POST
    path('status/', check_status, name='check_status'),# Ofise giriş durumu GET
    path('weekly/', user_attendance_weekly, name='attendance_weekly'),  # Haftalık kayıtlar(PERSONEL DASHBOARD) GET
     path('datatable/', server_side_attendance, name='server_side_attendance'),

    
    
]
