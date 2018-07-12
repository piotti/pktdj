from django.urls import path, include

from . import views


app_name='dj'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('info/', views.info, name='info'),
    # path(r'^queue/(?P<song_id>\w+)$', views.queue, name='queue'),
    path('vote/<song_id>/', views.vote, name='vote'),
    # path('^next/$', views.next, name='next'),
    path('feedback/', views.feedback, name='feedback'),
    path('feedback/submit/', views.feedback_submit, name='feedback_submit'),
    path('djadmin/', views.admin, name='admin'),
    path('djadmin/setindex/', views.setindex, name='setindex'),
    path('djadmin/reset/', views.reset, name='reset'),
    path('djadmin/start/', views.start, name='start'),
    path('djadmin/stop/', views.stop, name='stop'),
    path('dj/login/', views.login, name='login'),
    path('dj/logout/', views.logout, name='logout'),
    # path(r'^remove/(?P<song_id>\w+)$', views.remove, name='remove'),
]
