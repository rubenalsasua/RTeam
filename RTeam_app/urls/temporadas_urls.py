from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('temporadas/', views.TemporadaListView.as_view(), name='temporada_list'),
    path('temporadas/crear/', views.TemporadaCreateView.as_view(), name='temporada_create'),
    path('temporadas/<int:pk>/', views.TemporadaDetailView.as_view(), name='temporada_detail'),
    path('temporadas/<int:pk>/editar/', views.TemporadaUpdateView.as_view(), name='temporada_update'),
    path('temporadas/<int:pk>/eliminar/', views.TemporadaDeleteView.as_view(), name='temporada_delete'),
]
