from django.urls import path
from . import views

urlpatterns = [
    path('home/',views.home),
    path('success/', views.skull_input, name='skull_input'),
        path('points/', views.points)
]
