from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('webhook/', views.webhook, name='webhook'),
    path('get_profile', views.get_profile, name='get_profile'),
    path('update_profile', views.update_profile, name='update_profile'),
]