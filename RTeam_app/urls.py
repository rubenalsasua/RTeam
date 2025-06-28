from django.urls import path
from RTeam_app import views
urlpatterns = [
    path('', views.index, name='index'),
]