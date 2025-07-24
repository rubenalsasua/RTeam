from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('entrenadores/', views.EntrenadorListView.as_view(), name='entrenador_list'),
    path('entrenadores/<int:pk>/', views.EntrenadorDetailView.as_view(), name='entrenador_detail'),
    path('entrenadores/crear/', views.EntrenadorCreateView.as_view(), name='entrenador_create'),
    path('entrenadores/<int:pk>/editar/', views.EntrenadorUpdateView.as_view(), name='entrenador_update'),
    path('entrenadores/<int:pk>/eliminar/', views.EntrenadorDeleteView.as_view(), name='entrenador_delete'),
]
