from django.urls import path
from .import views

app_name = 'leads_api'

urlpatterns = [
    path('leads/', views.LeadListCreateAPIView.as_view(), name='lead_list_create'),
    path('leads/<int:pk>/', views.LeadRetrieveUpdateDestroyAPIView.as_view(),
         name='lead_retrieve_update_destroy'),
]
