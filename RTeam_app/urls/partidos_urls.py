from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('partidos/', views.PartidoListView.as_view(), name='partido_list'),
]
