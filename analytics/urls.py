from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.GeneralReport.as_view(), name='general_report'),
    path('managers/', views.ManagerReport.as_view(), name='manager_report'),
    path('period/', views.PeriodReport.as_view(), name='period_report'),
]
