from django.urls import path
from . import views


urlpatterns = [
    path('', views.OrganizationList, name='organization_list'),
    path('create/', views.OrganizationCreateView.as_view(), name='organization_create'),
    path('invite/', views.OrganizationInviteView.as_view(), name='organization_invite'),
    path('join/<str:token>/', views.OrganizationJoinView.as_view(), name='organization_join'),
]
