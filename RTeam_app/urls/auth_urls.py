from django.urls import path
from RTeam_app import views

urlpatterns = [
    path('', views.sign_in, name='sign_in'),
    path('sign-out/', views.sign_out, name='sign_out'),
    path('auth-receiver/', views.auth_receiver, name='auth_receiver'),
    path('google-auth/', views.AuthGoogle.as_view(), name='google_auth'),
]
