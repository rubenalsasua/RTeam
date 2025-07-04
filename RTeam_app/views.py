from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Temporada, Liga, Equipo, Jugador, JugadorEquipoTemporada, Entrenador, EntrenadorEquipoTemporada


# Create your views here.
def index(request):
    return render(request, 'base.html')


class TemporadaListView(ListView):
    model = Temporada
    template_name = 'temporada_list.html'
    context_object_name = 'temporadas'


class LigaListView(ListView):
    model = Liga
    template_name = 'liga_list.html'
    context_object_name = 'ligas'


class EquipoListView(ListView):
    model = Equipo
    template_name = 'equipo_list.html'
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


class JugadorListView(ListView):
    model = Jugador
    template_name = 'jugador_list.html'
    context_object_name = 'jugadores'


class JugadorDetailView(DetailView):
    model = Jugador
    template_name = 'jugador_detail.html'
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


class EntrenadorListView(ListView):
    model = Entrenador
    template_name = 'entrenador_list.html'
    context_object_name = 'entrenadores'


class EntrenadorDetailView(DetailView):
    model = Entrenador
    template_name = 'entrenador_detail.html'
    context_object_name = 'entrenador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temporadas_info = EntrenadorEquipoTemporada.objects.filter(
            entrenador=self.object
        ).select_related('equipo', 'temporada').order_by('-temporada__periodo')
        context['temporadas_info'] = temporadas_info
        return context
