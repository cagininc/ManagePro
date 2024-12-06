from datetime import time, timedelta, date, timezone
from django.utils import timezone
from django.shortcuts import render
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from attendance.models import Attendance
from django.core.paginator import Paginator
from django.db.models import Q
from notifications.utils import send_notification
from user.models import CustomUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_office_status(request):
    """
    Kullanıcının ofiste olup olmadığını kontrol eder
    """
    user = request.user
    today= date.today()
    attendance = Attendance.objects.filter(user=user,date=today).last()
    if attendance and attendance.check_in and not attendance.check_out:
        return Response({'isCheckedIn':True})# personel hala ofiste(çıkış yapmadı)
    else:
        #Kullanıcı ofiste değil 
        return Response({'isCheckedIn':False})
    
    




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_attendance_list(request):
    """
    Kullanıcının giriş-çıkış kayıtlarını döndürür.
    """
    user = request.user
    if user.role != 'personel':
        return Response({"error": "Bu sayfaya yalnızca personeller erişebilir."}, status=403)

    attendance_records = Attendance.objects.filter(user=user).order_by('-created_at')
    attendance_data = [
        {
            "check_in_time": record.check_in_time,
            "check_out_time": record.check_out_time,
            "date": record.created_at.strftime('%Y-%m-%d'),
        }
        for record in attendance_records
    ]

    return Response(attendance_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_in(request):
    user = request.user
    print(f"[DEBUG] Received check-in request from user: {user.username}")

    today = timezone.now().date()
    print(f"[DEBUG] Today's date: {today}")

    # Aynı gün için zaten check-in yapılmış mı kontrol
    attendance, created = Attendance.objects.get_or_create(user=user, date=today)
    print(f"[DEBUG] Attendance record status - Created: {created}")

    # Eğer check-in zaten varsa hata döndür
    if attendance.check_in:
        print(f"[DEBUG] User {user.username} has already checked in today at {attendance.check_in}")
        return Response({"message": "Bugün zaten ofise giriş yaptınız."}, status=400)

    # Şu anki zamanı al ve check-in saatine kaydet
    check_in_time = timezone.now()
    print(f"[DEBUG] Current check-in time: {check_in_time}")

    attendance.check_in = check_in_time.time()
    attendance.save()
    print(f"[DEBUG] Check-in time saved for user: {user.username} at {attendance.check_in}")

    # Sabah geç kalma saati - örneğin 08:30
    office_start_time = time(8, 30)
    print(f"[DEBUG] Office start time: {office_start_time}")

    # Geç kalma kontrolü
    if check_in_time.time() > office_start_time:
        # Admin kullanıcılarını bul ve WebSocket ile bildirim gönder
        admin_users = CustomUser.objects.filter(role='Admin')
    channel_layer = get_channel_layer()
    if not channel_layer:
        print(f"[ERROR] Channel layer is None. WebSocket notifications cannot be sent.")
        return Response({"message": "Bildirim sistemi çalışmıyor. Lütfen sistem yöneticisiyle iletişime geçin."}, status=500)

    print(f"[DEBUG] Channel layer acquired successfully.")

    for admin in admin_users:
            message = f"{user.username} is late tooday."
            print(f"[DEBUG] Preparing to send notification to admin: {admin.username}")

            try:
                # Bildirim gönderme işlemi
                async_to_sync(channel_layer.group_send)(
                    "managers_notifications",
                    {
                        "type": "notification_message",
                        "message": message,
                    }
                )
                # Eğer bu satır başarılı bir şekilde çalışırsa bu log gözükecek
                print(f"[DEBUG] Notification successfully sent to admin: {admin.username}")

            except Exception as e:
                # Eğer bir hata oluşursa, bu log ile hatayı gösterebiliriz
                print(f"[ERROR] Failed to send notification to admin: {admin.username}. Error: {str(e)}")

    return Response({"message": "Ofise giriş kaydedildi."}, status=200)
        
#checkout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_out(request):
    user = request.user
    today = now().date()

    try:
        attendance = Attendance.objects.get(user=user, date=today)
    except Attendance.DoesNotExist:
        return Response({"message": "Bugün için check-in bulunamadı."}, status=400)

    if attendance.check_out:
        return Response({"message": "Bugün zaten çıkış yaptınız."}, status=400)

    attendance.check_out = now().time()
    attendance.save()
    return Response({"message": "Ofisten çıkış kaydedildi."}, status=200)

# Kullanıcı ofiste bulunma durumu kontrol
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_status(request):
    """
    Kullanıcının güncel ofis durumu: check_in veya check_out yapıldı mı?
    """
    user = request.user
    today = now().date()

    try:
        attendance = Attendance.objects.get(user=user, date=today)
        if attendance.check_in and not attendance.check_out:
            return Response({"status": "checked_in"}, status=200)  # Ofiste
        elif attendance.check_out:
            return Response({"status": "checked_out"}, status=200)  # Çıkış yapmış
        else:
            return Response({"status": "not_checked_in"}, status=200)  # Hiç giriş yapmamış
    except Attendance.DoesNotExist:
        return Response({"status": "not_checked_in"}, status=200)
# Ofiste geçirilen süreyi formatlama
def format_duration(duration):
    """
    Ofiste geçirilen süreyi HH:MM formatına dönüştürür.
    """
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)  #saniye kısmına ihtiyacımız yok 
    return f"{hours:02}:{minutes:02}"
# Personel dashboard weekly report
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_attendance_weekly(request):
    user = request.user
    today = now().date()
    last_week = today - timedelta(days=7)

    attendance_records = Attendance.objects.filter(user=user, date__range=[last_week, today]).order_by('-date')
    attendance_data = [
        {
            "date": record.date.strftime('%Y-%m-%d'),
            "check_in": record.check_in.strftime('%H:%M') if record.check_in else None,
            "check_out": record.check_out.strftime('%H:%M') if record.check_out else None,
            "duration": format_duration(record.office_duration) if record.office_duration else None
        }
        for record in attendance_records
    ]
    return Response(attendance_data)



# Yönetici dashboard server-side dataTable
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def server_side_attendance(request):
    """
    Server-side DataTable için verileri döner.
    """
    draw = request.GET.get('draw', 1)
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    order_column = request.GET.get('order[0][column]', 0)
    order_dir = request.GET.get('order[0][dir]', 'asc')

    columns = ['user__username', 'date', 'check_in', 'check_out', 'office_duration', 'late_duration']
    order_by = columns[int(order_column)] if order_column.isdigit() and int(order_column) < len(columns) else 'date'
    if order_dir == 'desc':
        order_by = f'-{order_by}'

    records = Attendance.objects.filter(
        Q(user__username__icontains=search_value) | 
        Q(date__icontains=search_value)
    ).order_by(order_by)

    paginator = Paginator(records, length)
    page_number = (start // length) + 1
    page = paginator.get_page(page_number)

    data = [
        {
            "user": record.user.username,
            "date": record.date.strftime('%Y-%m-%d'),
            "check_in": record.check_in.strftime('%H:%M') if record.check_in else "-",
            "check_out": record.check_out.strftime('%H:%M') if record.check_out else "-",
            "office_duration": format_duration(record.office_duration) if record.office_duration else "-",
            "late_duration": str(record.late_duration),
        }
        for record in page.object_list
    ]

    response = {
        "draw": draw,
        "recordsTotal": records.count(),
        "recordsFiltered": records.count(),
        "data": data,
    }

    return Response(response)
