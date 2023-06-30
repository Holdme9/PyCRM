from django.urls import path, include
from . import views

app_name = 'organizations'


urlpatterns = [
    path('', views.OrganizationList, name='organization_list'),
    path('create/', views.OrganizationCreateView.as_view(), name='organization_create'),
    path('invite/', views.OrganizationInviteView.as_view(), name='organization_invite'),
    path('join/<str:token>/', views.OrganizationJoinView.as_view(), name='organization_join'),
    path('<int:org_id>/leads/', include(('leads.urls', 'leads'), namespace='leads')),
    path('<int:org_id>/analytics/', include(('analytics.urls', 'analytics'), namespace='analytics'))
]
