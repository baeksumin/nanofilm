from django.urls import path
from . import views

urlpatterns = [
    path('take/', views.take), 
    path('composite/', views.composite), 
]