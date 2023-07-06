from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .import views

app_name = 'users_api'

urlpatterns = [
    path('signup/', views.SignupAPIView.as_view(), name='user_signup'),
    path('get-auth-token/', obtain_auth_token, name='get_auth_token'),
]
