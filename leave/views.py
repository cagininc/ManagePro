from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from leave.models import Leave
from rest_framework import status as http_status

from .serializers import LeaveStatusUpdateSerializer


class LeavePagination(PageNumberPagination):
    """
    İzin talepleri için sayfalama ayarları.
    """
    page_size = 10  # Sayfa başına kayıt sayısı
    page_size_query_param = 'length'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_leave_list(request):
    """
    Giriş yapan kullanıcının izinlerini döndürür.
    """
    user = request.user
    leaves = Leave.objects.filter(user=user).order_by('-start_date')

    leave_data = [
        {
            "start_date": leave.start_date.strftime('%Y-%m-%d'),
            "end_date": leave.end_date.strftime('%Y-%m-%d'),
            "reason": leave.reason,
            "status": leave.get_status_display()
        }
        for leave in leaves
    ]

    return Response(leave_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_leave_request(request):
    """
    Kullanıcının izin talebi oluşturması.
    """
    user = request.user
    data = request.data

    start_date = data.get('start_date')
    end_date = data.get('end_date')
    reason = data.get('reason')

    if not start_date or not end_date or not reason:
        return Response({"error": "Tüm alanlar zorunludur."}, status=400)

    if start_date > end_date:
        return Response({"error": "Başlangıç tarihi, bitiş tarihinden sonra olamaz."}, status=400)

    leave = Leave.objects.create(user=user, start_date=start_date, end_date=end_date, reason=reason)
    return Response({"message": "İzin talebi başarıyla oluşturuldu.", "leave_id": leave.id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_leave_requests(request):
    """
    Tüm izin taleplerini listeleyen endpoint.
    """
    if not request.user.is_staff:
        return Response({"error": "Bu işlem için yetkiniz yok."}, status=403)

    leaves = Leave.objects.select_related('user').order_by('-start_date')
    paginator = LeavePagination()
    paginated_leaves = paginator.paginate_queryset(leaves, request)

    leave_data = [
        {
            "id": leave.id,
            "username": leave.user.username,
            "start_date": leave.start_date.strftime('%Y-%m-%d'),
            "end_date": leave.end_date.strftime('%Y-%m-%d'),
            "reason": leave.reason,
            "status": leave.get_status_display(),
            "remaining_leave_days": leave.user.remaining_leave_days,  # 

        }
        for leave in paginated_leaves
    ]

    return Response({
        "draw": int(request.GET.get("draw", 1)),  # DataTables için draw parametresi
        "recordsTotal": leaves.count(),
        "recordsFiltered": leaves.count(),
        "data": leave_data
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_leave_status(request, leave_id):
    """
    Belirli bir izin talebinin durumunu günceller ve kalan izin günlerini azaltır.
    """
    if not request.user.is_staff:
        return Response({"error": "Bu işlem için yetkiniz yok."}, status=http_status.HTTP_403_FORBIDDEN)

    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        return Response({"error": "İzin talebi bulunamadı."}, status=http_status.HTTP_404_NOT_FOUND)

    print("Gelen request.data:", request.data)  # Gelen veriyi kontrol etmek için
    serializer = LeaveStatusUpdateSerializer(leave, data=request.data, partial=True)

    if serializer.is_valid():
        new_status = serializer.validated_data.get('status')
        print("Serializer doğrulandı, yeni status:", new_status)  # Serializer doğrulandıktan sonra status değerini kontrol etmek için

        # Eğer durum "approved" olarak değiştiriliyorsa
        if new_status == "approved" and leave.status != "approved":
            user = leave.user
            days = (leave.end_date - leave.start_date).days + 1

            # Kalan izin günlerini kontrol et
            if user.remaining_leave_days >= days:
                user.remaining_leave_days -= days
                user.save()

                # Eğer kalan izin günleri 3 veya daha az ise bildirim
                if user.remaining_leave_days <= 3:
                    print(f"Uyarı: {user.username} için kalan izin günleri kritik seviyede: {user.remaining_leave_days}")
            else:
                print("Yeterli izin günü yok, işlem reddedildi.")  # Yeterli izin günleri olmadığında
                return Response({"error": "Yeterli izin günü yok."}, status=http_status.HTTP_400_BAD_REQUEST)

        leave.status = new_status
        leave.save()
        print(f"İzin talebi '{leave.get_status_display()}' olarak güncellendi.")  # Başarıyla güncellenen izin talebi

        return Response({"message": f"İzin talebi '{leave.get_status_display()}' olarak güncellendi."})

    # Serializer hatası varsa, hatayı loglayalım
    print("Serializer hataları:", serializer.errors)
    return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
