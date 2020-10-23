from django.urls import path
from . import views
form . import reply

urlpatterns = [
    path('', views.index, name='index'),
    #path('get_profile', views.get_profile, name='get_profile'),
    path('get_history', views.get_history, name='get_history'),
    path('get_app', views.get_application_by_case_id, name='get_app'),
    path('search_case', views.search_case, name='search_case'),
    path('get_case', views.get_case_by_case_id, name='get_case'),
    path('crud_profile', views.crud_profile, name='crud_profile'),
    path('crud_case', views.crud_case, name='crud_case'),
    path('crud_app', views.crud_application, name='crud_app'),
    path('callback', reply.callback, name='callback')

]