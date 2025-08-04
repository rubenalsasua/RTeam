from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('campos/', views.CampoListView.as_view(), name='campo_list'),
    path('campos/crear/', views.CampoCreateView.as_view(), name='campo_create'),
    path('campos/<int:pk>/', views.CampoDetailView.as_view(), name='campo_detail'),
    path('campos/<int:pk>/editar/', views.CampoUpdateView.as_view(), name='campo_update'),
    path('campos/<int:pk>/eliminar/', views.CampoDeleteView.as_view(), name='campo_delete'),
]