from django.urls import path
from . import views

urlpatterns = [
    path('home/',views.home),
    path('success/<point_cloud_array>/', views.skull_input, name='skull_input')
]
