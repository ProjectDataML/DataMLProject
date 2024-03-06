from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(r'stats/', views.stats, name='stats'),
    path(r'ml/', views.ml, name='ml'),
]