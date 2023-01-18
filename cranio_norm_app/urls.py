from django.urls import path
from . import views

urlpatterns = [
    path('home/',views.home),
    path('file_upload/',views.file_upload)
]
