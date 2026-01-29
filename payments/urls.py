from django.urls import path
from . import views


urlpatterns = [
    path('process/', views.process_payment, name='process_payment'),
    path('create/', views.create_payment, name='create_payment'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('history/', views.payment_history, name='payment_history'),
    path('detail/<str:bill_number>/', views.payment_detail, name='payment_detail'),
    path('webhook/', views.payment_webhook, name='payment_webhook'),
]
