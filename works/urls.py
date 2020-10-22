from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_profile', views.get_profile, name='get_profile'),
    path('get_history', views.get_history, name='get_history'),
    path('get_app', views.get_application_by_case_id, name='get_app'),
    
]