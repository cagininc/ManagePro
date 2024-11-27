from django.contrib import admin
from .models import Leave

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'leave_duration', 'status', 'reason', 'created_at')
    list_filter = ('status', 'start_date', 'end_date', 'user')
    search_fields = ('user__username', 'reason')
