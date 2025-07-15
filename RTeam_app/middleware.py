from django.contrib import admin
from django.shortcuts import redirect
from django.urls import resolve
from django.utils import timezone
from RTeam_app.models import Profile


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


class LastVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Actualizar last_visit en Profile en lugar de last_login en User
            profile = Profile.objects.filter(user=request.user).first()
            if profile:
                # Solo actualiza si ha pasado al menos 1 minuto desde la última actualización
                # para evitar múltiples actualizaciones en la misma visita
                if not profile.last_visit or (timezone.now() - profile.last_visit).seconds > 60:
                    profile.last_visit = timezone.now()
                    profile.save(update_fields=['last_visit'])

        response = self.get_response(request)
        return response
