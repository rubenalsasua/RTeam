from django.contrib import admin
from django.shortcuts import redirect
from django.urls import resolve


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Comprobar si la URL solicitada está en el admin site
        resolved = resolve(request.path)
        if resolved.app_name == 'admin' and resolved.url_name != 'login':
            # Verificar si el usuario tiene el rol ADMIN
            if not request.user.is_authenticated:
                return redirect('sign_in')

            if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
                # Redirigir a la página de inicio si no tiene el rol adecuado
                return redirect('index')

        return self.get_response(request)