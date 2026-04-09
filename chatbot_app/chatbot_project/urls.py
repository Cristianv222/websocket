from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.path),
    path('', include('chat.urls')),
]
