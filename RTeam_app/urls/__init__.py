from django.urls import path, include
from RTeam_app import views

urlpatterns = [
    path('', include('RTeam_app.urls.auth_urls')),
    path('inicio/', views.index, name='index'),
    path('equipos_menu/', views.equipos_menu, name='equipos_menu'),
    path('', include('RTeam_app.urls.entrenadores_urls')),
    path('', include('RTeam_app.urls.equipos_urls')),
    path('', include('RTeam_app.urls.jugadores_urls')),
    path('', include('RTeam_app.urls.ligas_urls')),
    path('', include('RTeam_app.urls.partidos_urls')),
    path('', include('RTeam_app.urls.temporadas_urls')),
    path('', include('RTeam_app.urls.usuarios_urls')),
    path('', include('RTeam_app.urls.campos_urls')),
    path('serviceworker.js', views.service_worker, name='serviceworker'),

]
