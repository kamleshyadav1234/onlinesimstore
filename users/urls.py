from django.urls import path
from .views import (
   CustomLogoutView,
    ProfileView, ProfileUpdateView, DashboardView,
    PlanHistoryView, FavouritePlansView, UnifiedAuthView, delete_account, update_profile_picture
)

from django.contrib.auth import views as auth_views


urlpatterns = [
    path('auth/', UnifiedAuthView.as_view(), name='auth'),
    path('login/', UnifiedAuthView.as_view(), name='login'),  # Alias for backward compatibility
    # path('send-otp/', OTPSendView.as_view(), name='send_otp'),
    # path('verify-otp/', OTPVerifyView.as_view(), name='verify_otp'),
    # path('resend-otp/', OTPResendView.as_view(), name='resend_otp'),
    path('logout/',CustomLogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('plan-history/', PlanHistoryView.as_view(), name='plan_history'),
    path('favourites/', FavouritePlansView.as_view(), name='favourite_plans'),
    # Alternative using class-based view:
    # path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    
    path('profile/picture/', update_profile_picture, name='update_profile_picture'),
    path('profile/delete/', delete_account, name='delete_account'),
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change.html',
             success_url='/users/profile/'
         ), 
         name='password_change'),
    
     # Password reset URLs
        path('password_reset/', 
             auth_views.PasswordResetView.as_view(
                 template_name='users/password_reset.html',
                 email_template_name='users/password_reset_email.html',
                 subject_template_name='users/password_reset_subject.txt'
             ), 
             name='password_reset'),
        path('password_reset/done/', 
             auth_views.PasswordResetDoneView.as_view(
                 template_name='users/password_reset_done.html'
             ), 
             name='password_reset_done'),
        path('reset/<uidb64>/<token>/', 
             auth_views.PasswordResetConfirmView.as_view(
                 template_name='users/password_reset_confirm.html'
             ), 
             name='password_reset_confirm'),
        path('reset/done/', 
             auth_views.PasswordResetCompleteView.as_view(
                 template_name='users/password_reset_complete.html'
             ), 
             name='password_reset_complete'),
    
]