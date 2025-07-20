from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import JugadorForm
from RTeam_app.models import Jugador, JugadorEquipoTemporada
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


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
