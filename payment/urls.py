from django.urls import path
from .views import InitiatePaymentView, VerifyPaymentView, WebhookPaymentNotificationView

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('verify/', VerifyPaymentView.as_view(), name='payment-verify'),
    path('webhook/', WebhookPaymentNotificationView.as_view(), name='payment-webhook'),  # NEW
]
