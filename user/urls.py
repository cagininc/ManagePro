from django.urls import path
from .views import (user_profile,yonetici_login,yonetici_dashboard,personel_login,personel_dashboard,ofise_giris,
)

urlpatterns =[
    path('profile/', user_profile, name='user_profile'),  # profile page
    path('yonetici/login/', yonetici_login, name='yonetici_login'),
    path('yonetici/dashboard/', yonetici_dashboard, name='yonetici_dashboard'),
    path('personel/login/', personel_login, name='personel_login'),
    path('personel/dashboard/', personel_dashboard, name='personel_dashboard'),
    path('ofise/giris/', ofise_giris, name='ofise_giris'),
    
    
    
]