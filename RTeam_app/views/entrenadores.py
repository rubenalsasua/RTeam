from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import EntrenadorForm
from RTeam_app.models import Entrenador
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


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
