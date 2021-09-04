from django.urls import path, include
from . import views

app_name = 'game'
urlpatterns = [
    path('', views.GameList.as_view()),
    path('game/<int:pk>/', views.GameView.as_view(), name='game-view'),
    path('player/<str:name>/', views.PlayerView.as_view(), name='player-view'),
]
