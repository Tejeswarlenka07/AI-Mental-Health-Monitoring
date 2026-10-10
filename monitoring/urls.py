
from django.urls import path

from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mood/', views.mood, name='mood'),
    path('sleep/', views.sleep, name='sleep'),
    path('journal/', views.journal, name='journal'),
    path('stress/', views.stress, name='stress'),
    path('breathing/', views.breathing, name='breathing'),
    path("heart-rate/", views.heart_rate, name="heart_rate"),
    path("heart-rate-api/", views.heart_rate_api, name="heart_rate_api"),
    path('distress-prediction/', views.distress_prediction, name='distress_prediction'),
    path('recommendations/',views.recommendations,name='recommendations'),
    path('recommendation-history/',views.recommendation_history,name='recommendation_history'),
    path('recommendation-history/delete/<int:id>/',views.delete_recommendation,name='delete_recommendation'),
    path(
    'recommendation-history/clear/',
    views.clear_recommendation_history,
    name='clear_recommendation_history'
),
    path('facial-expression/', views.facial_expression, name='facial_expression'),
]

