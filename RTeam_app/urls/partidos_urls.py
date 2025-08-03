from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('partidos/', views.PartidoListView.as_view(), name='partido_list'),
    path('partidos/<int:pk>/', views.PartidoDetailView.as_view(), name='partido_detail'),
    path('partidos/create/<int:liga_id>/', views.PartidoCreateView.as_view(), name='partido_create'),
    path('partidos/<int:partido_id>/equipo/<int:equipo_id>/convocatoria/',
         views.ConvocatoriaListView.as_view(), name='convocatoria_list'),
    path('partidos/<int:partido_id>/equipo/<int:equipo_id>/convocatoria/crear/',
         views.ConvocatoriaCreateView.as_view(), name='convocatoria_create'),
    path('convocatoria/<int:pk>/eliminar/',
         views.ConvocatoriaDeleteView.as_view(), name='convocatoria_delete'),
    path('partidos/<int:partido_id>/equipo/<int:equipo_id>/convocatoria/exportar/',
         views.exportar_convocatoria, name='convocatoria_exportar'),
]
