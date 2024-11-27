from django.urls import path
from .views import (
    user_leave_list,
    create_leave_request,
    all_leave_requests,
    update_leave_status,
)

urlpatterns = [
    # Kullanıcı izin taleplerini listeleme
    path("list/", user_leave_list, name="user_leave_list"),  
    
    # Yeni izin talebi oluşturma
    path("create/", create_leave_request, name="create_leave_request"),  
    
    # Tüm izin taleplerini listeleme (yönetici yetkisiyle)
    path("requests/", all_leave_requests, name="all_leave_requests"),  
    
    # Belirli bir izin talebinin durumunu güncelleme
    path("update/<int:leave_id>/", update_leave_status, name="update_leave_status"),  
    
    # Belirli bir izin talebini yönetme (örneğin, onaylama veya reddetme)
    # path("requests/<int:leave_id>/manage/", manage_leave_request, name="manage_leave_request"),
]
