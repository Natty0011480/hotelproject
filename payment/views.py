from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import PaymentNotificationSerializer
from .models import Payment
from .serializers import PaymentSerializer
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
import requests
import uuid


@method_decorator(csrf_exempt, name='dispatch')
class InitiatePaymentView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        gateway = request.data.get('gateway', 'telebirr')  # default fallback
        transaction_id = str(uuid.uuid4())

        # 1. Call Node.js SuperApp API
        try:
            response = requests.post("http://localhost:3001/api/order", json={
                "title": "Payment from Django",
                "amount": amount,
                "transaction_id": transaction_id
            })
            response.raise_for_status()
            superapp_response = response.json()
        except Exception as e:
            return Response({"error": "Payment gateway error", "details": str(e)}, status=502)

        # 2. Save locally
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            gateway=gateway,
            status='pending',
            transaction_id=transaction_id
        )

        return Response({
            "status": "initiated",
            "payment_id": payment.id,
            "transaction_id": transaction_id,
            "gateway_response": superapp_response
        }, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyPaymentView(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        success = request.data.get('success', False)

        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        payment.status = 'success' if success else 'failed'
        payment.save()
        return Response({'status': payment.status})


@method_decorator(csrf_exempt, name='dispatch')
class WebhookPaymentNotificationView(generics.GenericAPIView):
    permission_classes = []
    serializer_class = PaymentNotificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transaction_id = serializer.validated_data['transaction_id']
        new_status = serializer.validated_data['status']

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

        payment.status = new_status
        payment.save()
        return Response({'status': 'updated'}, status=status.HTTP_200_OK)
