from django.urls import path

from . import views

urlpatterns = [
    
    path('drones', views.drones, name='drones'),
    
]
