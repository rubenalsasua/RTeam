from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('jugadores/', views.JugadorListView.as_view(), name='jugador_list'),
    path('jugadores/<int:pk>/', views.JugadorDetailView.as_view(), name='jugador_detail'),
    path('jugadores/crear/', views.JugadorCreateView.as_view(), name='jugador_create'),
    path('jugadores/<int:pk>/editar/', views.JugadorUpdateView.as_view(), name='jugador_update'),
    path('jugadores/<int:pk>/eliminar/', views.JugadorDeleteView.as_view(), name='jugador_delete'),
]
