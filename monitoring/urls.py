from django.urls import path

from .views import (
    dashboard,
    mood,
    sleep,
    journal
)


urlpatterns = [

    path(
        '',
        dashboard,
        name='dashboard'
    ),

    path(
        'mood/',
        mood,
        name='mood'
    ),

    path(
        'sleep/',
        sleep,
        name='sleep'
    ),

    path(
        'journal/',
        journal,
        name='journal'
    ),

]