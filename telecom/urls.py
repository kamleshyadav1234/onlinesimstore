from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('operators/', OperatorListView.as_view(), name='operator_list'),
    path('operators/<int:pk>/', OperatorDetailView.as_view(), name='operator_detail'),
    path('search/', SearchView.as_view(), name='search'),
    path('coverage-check/', CoverageCheckView.as_view(), name='coverage_check'),
    
    path('new-connection/cancel/<str:tracking_id>/', CancelConnectionRequestView.as_view(), name='cancel_connection_request'),

   # Port Number URLs
    path('port-number/', PortNumberView.as_view(), name='port_number'),
    path('port-number/status/<str:tracking_id>/', PortRequestStatusView.as_view(), name='port_request_status'),
    path('port-number/history/', UserPortRequestHistoryView.as_view(), name='port_request_history'),
    path('new-connection/status/<str:tracking_id>/', NewConnectionStatusView.as_view(), name='new_connection_status'),
    # New Connection URLs
    path('new-connection/', NewConnectionView.as_view(), name='new_connection'),
    path('api/new-connection-plans/', GetNewConnectionPlansView.as_view(), name='api_new_connection_plans'),
    path('new-connection/status/<str:tracking_id>/', NewConnectionStatusView.as_view(), name='new_connection_status'),
    path('new-connection/history/',UserNewConnectionHistoryView.as_view(), name='new_connection_history'),
    
    # Plan URLs
    path('plans/', PlanListView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', PlanDetailView.as_view(), name='plan_detail'),
    path('port-number/status/<str:tracking_id>/', PortRequestStatusView.as_view(), name='port_request_status'),

    # API URLs
    path('api/port-in-plans/', GetPortInPlansView.as_view(), name='api_port_in_plans'),
    # path('api/new-connection-plans/', GetNewConnectionPlansView.as_view(), name='api_new_connection_plans'),
    path('api/check-mnp-eligibility/', CheckMNPEligibilityView.as_view(), name='check_mnp_eligibility'),
    path('api/check-port-request/<str:mobile_number>/', check_port_request, name='check_port_request'),
    # User History
    path('my-connections/', UserConnectionHistoryView.as_view(), name='user_connection_history'),


     # SIM Replacement URLs
    path('sim-replacement/', 
         SIMReplacementCreateView.as_view(), 
         name='sim_replacement_create'),
    
    path('sim-replacement/documents/', 
         SIMReplacementDocumentView.as_view(), 
         name='sim_replacement_documents'),
    
    path('sim-replacement/status/', 
         SIMReplacementStatusView.as_view(), 
         name='sim_replacement_status'),
    
    path('sim-replacement/status/<str:request_id>/', 
         SIMReplacementStatusView.as_view(), 
         name='sim_replacement_status_detail'),
    
    path('sim-replacement/track/', 
         SIMReplacementListView.as_view(), 
         name='sim_replacement_list'),
    
    path('sim-replacement/<int:pk>/', 
         SIMReplacementDetailView.as_view(), 
         name='sim_replacement_detail'),
    
    path('sim-replacement/<int:pk>/update/', 
         SIMReplacementUpdateView.as_view(), 
         name='sim_replacement_update'),
    
    path('sim-replacement/instructions/', 
         SIMReplacementInstructionsView.as_view(), 
         name='sim_replacement_instructions'),
]