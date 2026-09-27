from django.urls import path

from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mood/', views.mood, name='mood'),
    path('sleep/', views.sleep, name='sleep'),
    path('journal/', views.journal, name='journal'),
    path('stress/', views.stress, name='stress'),
    path('breathing/', views.breathing, name='breathing'),
]