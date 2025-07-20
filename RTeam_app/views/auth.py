import os
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout, login
from google.oauth2 import id_token
from google.auth.transport import requests
from RTeam_app.models import User, Profile
from decouple import config
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings


@csrf_exempt
def sign_in(request):
    return render(request, 'sign_in.html')


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    print('Inside')
    token = request.POST['credential']

    try:
        # Cambia esta línea para usar config() en lugar de os.environ
        from decouple import config
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), config('GOOGLE_OAUTH_CLIENT_ID')
        )
    except ValueError:
        return HttpResponse(status=403)

    # In a real app, I'd also save any new user here to the database.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    request.session['user_data'] = user_data

    return redirect('sign_in')


from django.contrib.auth import logout


def sign_out(request):
    # Eliminar datos de sesión personalizados
    if 'user_data' in request.session:
        del request.session['user_data']

    # Cerrar sesión de Django correctamente
    logout(request)

    return redirect('sign_in')


@method_decorator(csrf_exempt, name='dispatch')
class AuthGoogle(View):  # Cambia de APIView a View
    """
    Google calls this URL after the user has signed in with their Google account.
    """

    def get_google_user_data(self, request):
        if 'credential' not in request.POST:
            raise ValueError("No se proporcionó el token 'credential' en la solicitud")
        token = request.POST['credential']
        return id_token.verify_oauth2_token(
            token, requests.Request(), config('GOOGLE_OAUTH_CLIENT_ID')
        )

    def post(self, request, *args, **kwargs):
        try:
            user_data = self.get_google_user_data(request)
        except ValueError as e:
            # Log del error específico
            print(f"Error de verificación de token de Google: {str(e)}")
            return HttpResponse(f"Error de verificación: {str(e)}", status=403)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return HttpResponse(f"Error inesperado: {str(e)}", status=500)

        # Resto del código sin cambios...

        email = user_data["email"]

        # Obtener nombre completo de Google
        first_name = user_data.get("given_name", "")
        last_name = user_data.get("family_name", "")
        full_name = user_data.get("name", "")  # Nombre completo proporcionado por Google

        # Crear o actualizar usuario
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": first_name,
                "last_name": last_name,  # Guardar apellidos
            }
        )
        # Si es un usuario nuevo, enviar email de notificación
        if created:
            admin_email = config('ADMIN_EMAIL', default='')

            # Preparar datos para el email
            subject = 'Nuevo usuario registrado en RTeam'
            message = f"""
                Se ha registrado un nuevo usuario en RTeam:

                Nombre: {full_name}
                Email: {email}
                Fecha: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}
                IP: {request.META.get('REMOTE_ADDR', 'No disponible')}
                Navegador: {request.META.get('HTTP_USER_AGENT', 'No disponible')}
                """

            # Enviar el email
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error al enviar email de notificación: {e}")

        # Si el usuario ya existía, actualizamos sus datos por si han cambiado en Google
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Determinar el rol basado en el correo electrónico

        admin_email = config('ADMIN_EMAIL', default='')
        role = 'ADMIN' if email.lower() == admin_email.lower() else 'INVITADO'

        # Configurar is_staff si es administrador
        if role == 'ADMIN' and not user.is_staff:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        # Crear o actualizar el perfil
        from RTeam_app.models import Profile
        profile, profile_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'sign_up_method': 'google',
                'role': role,
                'full_name': full_name,  # Guardar nombre completo en el perfil
            }
        )

        # Si el usuario ya existía pero es el administrador, asegúrate de que tenga el rol correcto
        if not profile_created:
            if email.lower() == admin_email.lower() and profile.role != 'ADMIN':
                profile.role = 'ADMIN'
                if not user.is_superuser:
                    user.is_superuser = True
                    user.save()
                profile.save()
            # Actualizar el nombre completo por si ha cambiado
            if profile.full_name != full_name:
                profile.full_name = full_name
                profile.save()

        # Guardar datos en sesión y autenticar
        request.session['user_data'] = user_data
        from django.contrib.auth import login
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Redireccionar
        if 'pythonanywhere' in request.get_host():
            return redirect('https://rubenalsasua.pythonanywhere.com/inicio/')
        else:
            return redirect('index')
