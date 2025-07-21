from django.views.generic import ListView, UpdateView, DeleteView
from RTeam_app.forms import UsuarioForm
from RTeam_app.models import User, Profile
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import AdminRequiredMixin
from django.urls import reverse_lazy


class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return User.objects.all().order_by('username')


class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    def get(self, request, pk):
        usuario = Profile.objects.get(id=pk)
        formulario = UsuarioForm(instance=usuario)
        context = {'formulario': formulario, 'usuario': usuario}
        return render(request, "usuarios/usuario_update.html", context)

    def post(self, request, pk):
        # Guarda el usuario actual para mantener la sesión
        current_user = request.user

        # Obtiene y procesa el perfil a modificar
        usuario = Profile.objects.get(id=pk)
        formulario = UsuarioForm(instance=usuario, data=request.POST)

        if formulario.is_valid():
            # Guarda el perfil con todos sus campos
            profile = formulario.save()

            # Asegúrate de que el usuario actual sigue autenticado
            from django.contrib.auth import login
            login(request, current_user)

            # Añade mensaje de éxito
            from django.contrib import messages
            messages.success(request, "El perfil se actualizó correctamente")

            return redirect("usuario_list")

        return render(request, "usuarios/usuario_update.html",
                      {"formulario": formulario, 'usuario': usuario})


class UsuarioDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = User
    template_name = "usuarios/usuario_confirm_delete.html"
    context_object_name = 'usuario'
    success_url = reverse_lazy('usuario_list')


def perfil_view(request):
    if request.user.is_authenticated:
        usuario = Profile.objects.get(user=request.user)
        return render(request, "usuarios/usuario_detail.html", {'usuario': usuario})
    else:
        return redirect('login')
