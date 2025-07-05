from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('temporadas/', views.TemporadaListView.as_view(), name='temporada_list'),
    path('temporadas/crear/', views.TemporadaCreateView.as_view(), name='temporada_create'),
    path('temporadas/<int:pk>/editar/', views.TemporadaUpdateView.as_view(), name='temporada_update'),
    path('temporadas/<int:pk>/eliminar/', views.TemporadaDeleteView.as_view(), name='temporada_delete'),
    path('ligas/', views.LigaListView.as_view(), name='liga_list'),
    path('ligas/crear/', views.LigaCreateView.as_view(), name='liga_create'),
    path('ligas/<int:pk>/editar/', views.LigaUpdateView.as_view(), name='liga_update'),
    path('ligas/<int:pk>/eliminar/', views.LigaDeleteView.as_view(), name='liga_delete'),
    path('equipos/', views.EquipoListView.as_view(), name='equipo_list'),
    path('equipos/crear/', views.EquipoCreateView.as_view(), name='equipo_create'),
    path('equipos/<int:pk>/editar/', views.EquipoUpdateView.as_view(), name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', views.EquipoDeleteView.as_view(), name='equipo_delete'),

    path('jugadores/', views.JugadorListView.as_view(), name='jugador_list'),
    path('jugadores/<int:pk>/', views.JugadorDetailView.as_view(), name='jugador_detail'),
    path('jugadores/crear/', views.JugadorCreateView.as_view(), name='jugador_create'),
    path('jugadores/<int:pk>/editar/', views.JugadorUpdateView.as_view(), name='jugador_update'),
    path('jugadores/<int:pk>/eliminar/', views.JugadorDeleteView.as_view(), name='jugador_delete'),

    path('entrenadores/', views.EntrenadorListView.as_view(), name='entrenador_list'),
    path('entrenadores/<int:pk>/', views.EntrenadorDetailView.as_view(), name='entrenador_detail'),
    path('entrenadores/crear/', views.EntrenadorCreateView.as_view(), name='entrenador_create'),
    path('entrenadores/<int:pk>/editar/', views.EntrenadorUpdateView.as_view(), name='entrenador_update'),
    path('entrenadores/<int:pk>/eliminar/', views.EntrenadorDeleteView.as_view(), name='entrenador_delete'),

]
