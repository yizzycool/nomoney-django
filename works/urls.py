from django.urls import path
from works.views import *

urlpatterns = [
    path('get_history', get_history, name='get_history'),
    path('search_case', search_case, name='search_case'),
    path('get_case', get_case_by_case_id, name='get_case'),
    path('crud_profile', crud_profile, name='crud_profile'),
    path('crud_case', crud_case, name='crud_case'),
    path('crud_app', crud_application, name='crud_app'),
    path('callback', callback, name='callback'),
    #path('delete_hashtag', views.delete_hashtag, name='delete_hashtag')
]