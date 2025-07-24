from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('equipos/', views.EquipoListView.as_view(), name='equipo_list'),
    path('equipos/crear/', views.EquipoCreateView.as_view(), name='equipo_create'),
    path('equipos/<int:pk>/', views.EquipoDetailView.as_view(), name='equipo_detail'),
    path('equipos/<int:pk>/editar/', views.EquipoUpdateView.as_view(), name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', views.EquipoDeleteView.as_view(), name='equipo_delete'),
    path('equipos/<int:equipo_id>/agregar_jugador/', views.JugadorEquipoTemporadaCreateView.as_view(),
         name='jugador_equipo_create'),
    path('equipos/<int:equipo_id>/jugadores/<int:jugador_id>/eliminar/',
         views.JugadorEquipoTemporadaDeleteView.as_view(),
         name='jugador_en_equipo_delete'),
    path('equipos/<int:equipo_id>/agregar_entrenador/', views.EntrenadorEquipoTemporadaCreateView.as_view(),
         name='entrenador_equipo_create'),
    path('equipos/<int:equipo_id>/entrenadores/<int:entrenador_id>/eliminar/',
         views.EntrenadorEquipoTemporadaDeleteView.as_view(),
         name='entrenador_en_equipo_delete'),
]
