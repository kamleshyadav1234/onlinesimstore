from django.urls import path
from .views import (
    PlanListView, PlanDetailView, CategoryPlansView,
    ComparePlansView, ToggleFavouriteView
)

urlpatterns = [
    path('', PlanListView.as_view(), name='plan_list'),
    path('<int:pk>/', PlanDetailView.as_view(), name='plan_detail'),
    path('category/<str:category_slug>/', CategoryPlansView.as_view(), name='category_plans'),
    path('compare/', ComparePlansView.as_view(), name='compare_plans'),
    path('toggle-favourite/', ToggleFavouriteView.as_view(), name='toggle_favourite'),

]