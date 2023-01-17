from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('drones', views.drones, name='drones')
    
]
