import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from RTeam_project import settings
from .forms import TemporadaForm, LigaForm, EquipoForm, JugadorForm, EntrenadorForm, EquipoLigaTemporadaForm, \
    JugadorEquipoTemporadaForm, EntrenadorEquipoTemporadaForm, UsuarioForm
from .models import Temporada, Liga, Equipo, Jugador, JugadorEquipoTemporada, Entrenador, EntrenadorEquipoTemporada, \
    EquipoLigaTemporada, User, Profile

from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
            return redirect('index')
        return view_func(request, *args, **kwargs)

    return wrapper


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')


class TemporadaListView(LoginRequiredMixin, ListView):
    model = Temporada
    template_name = 'temporadas/temporada_list.html'
    context_object_name = 'temporadas'


class TemporadaDetailView(LoginRequiredMixin, DetailView):
    model = Temporada
    template_name = 'temporadas/temporada_detail.html'
    context_object_name = 'temporada'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ligas'] = Liga.objects.filter(
            temporada=self.object
        ).distinct()
        return context


class TemporadaCreateView(LoginRequiredMixin, CreateView):

    def get(self, request):
        formulario = TemporadaForm()
        context = {'formulario': formulario}
        return render(request, "temporadas/temporada_create.html", context)

    def post(self, request):
        formulario = TemporadaForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("temporada_list")
        return render(request, "temporadas/temporada_create.html", {"formulario": formulario})


class TemporadaUpdateView(LoginRequiredMixin, UpdateView):
    model = Temporada

    def get(self, request, pk):
        temporada = Temporada.objects.get(id=pk)
        formulario = TemporadaForm(instance=temporada)
        context = {'formulario': formulario, 'temporada': temporada}
        return render(request, "temporadas/temporada_update.html", context)

    def post(self, request, pk):
        temporada = Temporada.objects.get(id=pk)
        formulario = TemporadaForm(instance=temporada, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("temporada_list")
        return render(request, "temporadas/temporada_update.html", {"formulario": formulario, 'temporada': temporada})


class TemporadaDeleteView(LoginRequiredMixin, DeleteView):
    model = Temporada
    template_name = 'temporadas/temporada_confirm_delete.html'
    context_object_name = 'temporada'
    success_url = reverse_lazy('temporada_list')


class LigaListView(LoginRequiredMixin, ListView):
    model = Liga
    template_name = 'ligas/liga_list.html'
    context_object_name = 'ligas'


class LigaDetailView(LoginRequiredMixin, DetailView):
    model = Liga
    template_name = 'ligas/liga_detail.html'
    context_object_name = 'liga'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipos_liga'] = EquipoLigaTemporada.objects.filter(
            liga=self.object
        ).select_related('equipo')
        return context


class LigaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request):
        formulario = LigaForm()
        context = {'formulario': formulario}
        return render(request, "ligas/liga_create.html", context)

    def post(self, request):
        formulario = LigaForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("liga_list")
        return render(request, "ligas/liga_create.html", {"formulario": formulario})


class LigaUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, pk):
        liga = Liga.objects.get(id=pk)
        formulario = LigaForm(instance=liga)
        context = {'formulario': formulario, 'liga': liga}
        return render(request, "ligas/liga_update.html", context)

    def post(self, request, pk):
        liga = Liga.objects.get(id=pk)
        formulario = LigaForm(instance=liga, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("liga_list")
        return render(request, "ligas/liga_update.html", {"formulario": formulario, 'liga': liga})


class LigaDeleteView(LoginRequiredMixin, DeleteView):
    model = Liga
    template_name = 'ligas/liga_confirm_delete.html'
    context_object_name = 'liga'
    success_url = reverse_lazy('liga_list')


class EquipoListView(LoginRequiredMixin, ListView):
    model = Equipo
    template_name = 'equipos/equipo_list.html'
    context_object_name = 'equipos'

    def get_queryset(self):
        equipos = Equipo.objects.all().order_by('nombre')
        for equipo in equipos:
            equipo.temporadas_lista = Temporada.objects.filter(
                jugadorequipotemporada__equipo=equipo
            ).distinct()
            equipo.ligas_lista = Liga.objects.filter(
                equipoligatemporada__equipo=equipo
            ).distinct()
        return equipos


class EquipoDetailView(LoginRequiredMixin, DetailView):
    model = Equipo
    template_name = 'equipos/equipo_detail.html'
    context_object_name = 'equipo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jugadores'] = Jugador.objects.filter(
            jugadorequipotemporada__equipo=self.object
        ).distinct()
        context['entrenadores_info'] = EntrenadorEquipoTemporada.objects.filter(
            equipo=self.object
        ).select_related('entrenador')
        context['temporadas_ligas'] = EquipoLigaTemporada.objects.filter(
            equipo=self.object
        ).select_related('liga__temporada')
        return context


class EquipoCreateView(LoginRequiredMixin, CreateView):
    def get(self, request):
        formulario = EquipoForm()
        context = {'formulario': formulario}
        return render(request, "equipos/equipo_create.html", context)

    def post(self, request):
        formulario = EquipoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("equipo_list")
        return render(request, "equipos/equipo_create.html", {"formulario": formulario})


class EquipoUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, pk):
        equipo = Equipo.objects.get(id=pk)
        formulario = EquipoForm(instance=equipo)
        context = {'formulario': formulario, 'equipo': equipo}
        return render(request, "equipos/equipo_update.html", context)

    def post(self, request, pk):
        equipo = Equipo.objects.get(id=pk)
        formulario = EquipoForm(instance=equipo, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("equipo_list")
        return render(request, "equipos/equipo_update.html", {"formulario": formulario, 'equipo': equipo})


class EquipoDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipo
    template_name = 'equipos/equipo_confirm_delete.html'
    context_object_name = 'equipo'
    success_url = reverse_lazy('equipo_list')


class JugadorListView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'jugadores/jugador_list.html'
    context_object_name = 'jugadores'


class JugadorDetailView(LoginRequiredMixin, DetailView):
    model = Jugador
    template_name = 'jugadores/jugador_detail.html'
    context_object_name = 'jugador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temporadas_info = JugadorEquipoTemporada.objects.filter(
            jugador=self.object
        ).select_related('equipo', 'temporada').order_by('-temporada__periodo')

        context['temporadas_info'] = temporadas_info

        # Calcular estadísticas totales
        context['total_goles'] = sum(info.goles for info in temporadas_info)
        context['total_asistencias'] = sum(info.asistencias for info in temporadas_info)
        context['total_amarillas'] = sum(info.tarjetas_amarillas for info in temporadas_info)
        context['total_rojas'] = sum(info.tarjetas_rojas for info in temporadas_info)

        return context


class JugadorCreateView(LoginRequiredMixin, CreateView):
    def get(self, request):
        formulario = JugadorForm()
        context = {'formulario': formulario}
        return render(request, "jugadores/jugador_create.html", context)

    def post(self, request):
        formulario = JugadorForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("jugador_list")
        return render(request, "jugadores/jugador_create.html", {"formulario": formulario})


class JugadorUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, pk):
        jugador = Jugador.objects.get(id=pk)
        formulario = JugadorForm(instance=jugador)
        context = {'formulario': formulario, 'jugador': jugador}
        return render(request, "jugadores/jugador_update.html", context)

    def post(self, request, pk):
        jugador = Jugador.objects.get(id=pk)
        formulario = JugadorForm(instance=jugador, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("jugador_list")
        return render(request, "jugadores/jugador_update.html", {"formulario": formulario, 'jugador': jugador})


class JugadorDeleteView(LoginRequiredMixin, DeleteView):
    model = Jugador
    template_name = 'jugadores/jugador_confirm_delete.html'
    context_object_name = 'jugador'
    success_url = reverse_lazy('jugador_list')


class EntrenadorListView(LoginRequiredMixin, ListView):
    model = Entrenador
    template_name = 'entrenadores/entrenador_list.html'
    context_object_name = 'entrenadores'


class EntrenadorDetailView(LoginRequiredMixin, DetailView):
    model = Entrenador
    template_name = 'entrenadores/entrenador_detail.html'
    context_object_name = 'entrenador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temporadas_info = EntrenadorEquipoTemporada.objects.filter(
            entrenador=self.object
        ).select_related('equipo', 'temporada').order_by('-temporada__periodo')
        context['temporadas_info'] = temporadas_info
        return context


class EntrenadorCreateView(LoginRequiredMixin, CreateView):
    def get(self, request):
        formulario = EntrenadorForm()
        context = {'formulario': formulario}
        return render(request, "entrenadores/entrenador_create.html", context)

    def post(self, request):
        formulario = EntrenadorForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("entrenador_list")
        return render(request, "entrenadores/entrenador_create.html", {"formulario": formulario})


class EntrenadorUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, pk):
        entrenador = Entrenador.objects.get(id=pk)
        formulario = EntrenadorForm(instance=entrenador)
        context = {'formulario': formulario, 'entrenador': entrenador}
        return render(request, "entrenadores/entrenador_update.html", context)

    def post(self, request, pk):
        entrenador = Entrenador.objects.get(id=pk)
        formulario = EntrenadorForm(instance=entrenador, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("entrenador_list")
        return render(request, "entrenadores/entrenador_update.html",
                      {"formulario": formulario, 'entrenador': entrenador})


class EntrenadorDeleteView(LoginRequiredMixin, DeleteView):
    model = Entrenador
    template_name = 'entrenadores/entrenador_confirm_delete.html'
    context_object_name = 'entrenador'
    success_url = reverse_lazy('entrenador_list')


class EquipoLigaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request, liga_id):
        liga = Liga.objects.get(id=liga_id)
        equipos_existentes = liga.equipos.all()
        formulario = EquipoLigaTemporadaForm()
        formulario.fields['equipo'].queryset = Equipo.objects.exclude(id__in=equipos_existentes)

        context = {
            'formulario': formulario,
            'liga': liga
        }
        return render(request, "ligas/equipo_en_liga_create.html", context)

    def post(self, request, liga_id):
        liga = Liga.objects.get(id=liga_id)
        formulario = EquipoLigaTemporadaForm(data=request.POST)

        if formulario.is_valid():
            equipo_liga = formulario.save(commit=False)
            equipo_liga.liga = liga
            equipo_liga.save()
            return redirect("liga_detail", pk=liga_id)

        # Si hay errores, volver a mostrar el formulario
        equipos_existentes = liga.equipos.all()
        formulario.fields['equipo'].queryset = Equipo.objects.exclude(id__in=equipos_existentes)
        context = {
            'formulario': formulario,
            'liga': liga
        }
        return render(request, "ligas/equipo_en_liga_create.html", context)


class EquipoLigaDeleteView(LoginRequiredMixin, DeleteView):
    model = EquipoLigaTemporada
    template_name = 'ligas/equipo_en_liga_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipo'] = self.object.equipo
        context['liga'] = self.object.liga
        return context

    def get_success_url(self):
        return reverse_lazy('liga_detail', kwargs={'pk': self.object.liga.id})


class JugadorEquipoTemporadaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        # Obtener jugadores que no están en este equipo en la temporada actual
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        jugadores_existentes = equipo.jugadores.filter(
            jugadorequipotemporada__temporada=temporada_actual
        )

        formulario = JugadorEquipoTemporadaForm()
        formulario.fields['jugador'].queryset = Jugador.objects.exclude(id__in=jugadores_existentes)
        formulario.fields['temporada'].initial = temporada_actual

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "jugadores/jugador_en_equipo_create.html", context)

    def post(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        formulario = JugadorEquipoTemporadaForm(data=request.POST)

        if formulario.is_valid():
            jugador_equipo = formulario.save(commit=False)
            jugador_equipo.equipo = equipo
            jugador_equipo.save()
            return redirect("equipo_detail", pk=equipo_id)

        # Si hay errores, volver a mostrar el formulario
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        jugadores_existentes = equipo.jugadores.filter(
            jugadorequipotemporada__temporada=temporada_actual
        )
        formulario.fields['jugador'].queryset = Jugador.objects.exclude(id__in=jugadores_existentes)

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "jugadores/jugador_en_equipo_create.html", context)


class JugadorEquipoTemporadaDeleteView(LoginRequiredMixin, DeleteView):
    model = JugadorEquipoTemporada
    template_name = 'jugadores/jugador_en_equipo_confirm_delete.html'

    def get_object(self, queryset=None):
        jugador_id = self.kwargs.get('jugador_id')
        equipo_id = self.kwargs.get('equipo_id')
        return JugadorEquipoTemporada.objects.filter(
            jugador_id=jugador_id,
            equipo_id=equipo_id
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jugador'] = self.object.jugador
        context['equipo'] = self.object.equipo
        return context

    def get_success_url(self):
        return reverse_lazy('equipo_detail', kwargs={'pk': self.object.equipo.id})


class EntrenadorEquipoTemporadaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        # Obtener entrenadores que no están en este equipo en la temporada actual
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        entrenadores_existentes = equipo.entrenadores.filter(
            entrenadorequipotemporada__temporada=temporada_actual
        )

        formulario = EntrenadorEquipoTemporadaForm()
        formulario.fields['entrenador'].queryset = Entrenador.objects.exclude(id__in=entrenadores_existentes)
        formulario.fields['temporada'].initial = temporada_actual

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "entrenadores/entrenador_en_equipo_create.html", context)

    def post(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        formulario = EntrenadorEquipoTemporadaForm(data=request.POST)

        if formulario.is_valid():
            entrenador_equipo = formulario.save(commit=False)
            entrenador_equipo.equipo = equipo
            entrenador_equipo.save()
            return redirect("equipo_detail", pk=equipo_id)

        # Si hay errores, volver a mostrar el formulario
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        entrenadores_existentes = equipo.entrenadores.filter(
            entrenadorequipotemporada__temporada=temporada_actual
        )
        formulario.fields['entrenador'].queryset = Entrenador.objects.exclude(id__in=entrenadores_existentes)

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "entrenadores/entrenador_en_equipo_create.html", context)


class EntrenadorEquipoTemporadaDeleteView(LoginRequiredMixin, DeleteView):
    model = EntrenadorEquipoTemporada
    template_name = 'entrenadores/entrenador_en_equipo_confirm_delete.html'

    def get_object(self, queryset=None):
        entrenador_id = self.kwargs.get('entrenador_id')
        equipo_id = self.kwargs.get('equipo_id')
        return EntrenadorEquipoTemporada.objects.filter(
            entrenador_id=entrenador_id,
            equipo_id=equipo_id
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entrenador'] = self.object.entrenador
        context['equipo'] = self.object.equipo
        return context

    def get_success_url(self):
        return reverse_lazy('equipo_detail', kwargs={'pk': self.object.equipo.id})


def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'serviceworker.js')
    with open(sw_path, 'r') as file:
        content = file.read()
    return HttpResponse(content, content_type='application/javascript')


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
        token = request.POST['credential']
        from decouple import config
        return id_token.verify_oauth2_token(
            token, requests.Request(), config('GOOGLE_OAUTH_CLIENT_ID')
        )

    def post(self, request, *args, **kwargs):
        try:
            user_data = self.get_google_user_data(request)
        except ValueError:
            return HttpResponse("Invalid Google token", status=403)

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

        # Si el usuario ya existía, actualizamos sus datos por si han cambiado en Google
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Determinar el rol basado en el correo electrónico
        from decouple import config
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


class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return User.objects.all().order_by('username')


class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    def get(self, request, pk):
        usuario = Profile.objects.get(id=pk)
        formulario = UsuarioForm(instance=usuario)
        context = {'formulario': formulario, 'usuario': usuario}
        return render(request, "admin/usuario_update.html", context)

    def post(self, request, pk):
        # Guarda el usuario actual para mantener la sesión
        current_user = request.user

        # Obtiene y procesa el perfil a modificar
        usuario = Profile.objects.get(id=pk)
        formulario = UsuarioForm(instance=usuario, data=request.POST)

        if formulario.is_valid():
            # Guarda sin activar signals que puedan afectar la autenticación
            profile = formulario.save(commit=False)
            profile.save(update_fields=['role'])

            # Asegúrate de que el usuario actual sigue autenticado
            from django.contrib.auth import login
            login(request, current_user)

            return redirect("usuario_list")

        return render(request, "admin/usuario_update.html",
                      {"formulario": formulario, 'usuario': usuario})
