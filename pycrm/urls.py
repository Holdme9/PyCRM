"""
URL configuration for pycrm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from organizations.views import MainPage


urlpatterns = [
    path('adm/', admin.site.urls),
    path('', MainPage, name='main_page'),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('organizations/', include(('organizations.urls', 'organizations'),
                                   namespace='organizations')),
    path('users-api/', include(('users_api.urls', 'users_api'), namespace='users_api')),
]
