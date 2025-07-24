from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('ligas/', views.LigaListView.as_view(), name='liga_list'),
    path('ligas/crear/', views.LigaCreateView.as_view(), name='liga_create'),
    path('ligas/<int:pk>/', views.LigaDetailView.as_view(), name='liga_detail'),
    path('ligas/<int:pk>/editar/', views.LigaUpdateView.as_view(), name='liga_update'),
    path('ligas/<int:pk>/eliminar/', views.LigaDeleteView.as_view(), name='liga_delete'),
    path('ligas/<int:liga_id>/agregar_equipo/', views.EquipoLigaCreateView.as_view(), name='equipo_liga_create'),
    path('ligas/equipo/<int:pk>/eliminar/', views.EquipoLigaDeleteView.as_view(), name='equipo_en_liga_delete'),
]
