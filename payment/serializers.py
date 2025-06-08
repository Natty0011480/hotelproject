from rest_framework import serializers
from .models import  Payment
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at']

class PaymentNotificationSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    status = serializers.ChoiceField(choices=['success', 'failed'])