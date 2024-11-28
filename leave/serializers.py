from rest_framework import serializers
from leave.models import Leave

class LeaveSerializer(serializers.ModelSerializer):
    """
    İzin modelini tüm alanlarıyla serialize eden sınıf.
    """
    class Meta:
        model = Leave
        fields = '__all__'


class LeaveStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Kullanıcının izin talebinin durumunu güncellerken kullanılacak serializer.
    """
    class Meta:
        model = Leave
        fields = ['status']

    def validate_status(self, value):
        """
        Status alanının geçerli değer olup olmadığını kontrol eder.
        """
        if value not in ['approved', 'pending', 'rejected']:
            raise serializers.ValidationError("Geçersiz durum değeri.")
        return value
