from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('temporadas/', views.TemporadaListView.as_view(), name='temporada_list'),
    path('ligas/', views.LigaListView.as_view(), name='liga_list'),
    path('equipos/', views.EquipoListView.as_view(), name='equipo_list'),
    path('jugadores/', views.JugadorListView.as_view(), name='jugador_list'),
    path('jugadores/<int:pk>/', views.JugadorDetailView.as_view(), name='jugador_detail'),
    path('entrenadores/', views.EntrenadorListView.as_view(), name='entrenador_list'),
    path('entrenadores/<int:pk>/', views.EntrenadorDetailView.as_view(), name='entrenador_detail'),
]
