from django.views.generic import ListView, UpdateView
from RTeam_app.forms import UsuarioForm
from RTeam_app.models import User, Profile
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import AdminRequiredMixin


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
