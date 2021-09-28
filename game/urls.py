from django.urls import path, include
from . import views

app_name = 'game'
urlpatterns = [
    path('', views.GameList.as_view(), name='game-home'),
    path('statistics', views.Statistics.as_view(), name='game-stats'),
    path('live', views.GameList.as_view(), name='game-scores'),
    path('game/<int:pk>/', views.GameView.as_view(), name='game-view'),
    path('player/<int:slug>/', views.PlayerView.as_view(), name='player-view'),
    path('sever/<int:pk>/', views.GameServerView.as_view(), name='server-view'),
]
