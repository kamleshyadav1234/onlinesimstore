# admin_panel/urls.py
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # Users
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Plans
    path('plans/', views.plans_list, name='plans_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    
    # Payments
    path('payments/', views.payments_list, name='payments_list'),
    
    # Requests
    path('requests/pending/', views.pending_requests, name='pending_requests'),
    path('requests/<str:request_type>/<int:request_id>/action/', 
         views.request_action, name='request_action'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
]