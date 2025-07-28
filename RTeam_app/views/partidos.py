from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import TemporadaForm
from RTeam_app.models import Liga, Partido, Temporada
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class PartidoListView(LoginRequiredMixin, ListView):
    model = Partido
    template_name = 'partidos/partido_list.html'
    context_object_name = 'partidos'  # No se usará directamente, pero es buena práctica

    def get_queryset(self):
        # Obtener la liga seleccionada
        liga_id = self.request.GET.get('liga')
        temporada_actual = Temporada.objects.order_by('-periodo').first()

        # Obtener todas las ligas de la temporada
        ligas = Liga.objects.filter(temporada=temporada_actual).order_by('nombre')

        # Si no hay ligas, devolver queryset vacío
        if not ligas.exists():
            return Partido.objects.none()

        # Determinar la liga a mostrar
        if liga_id:
            liga_actual = get_object_or_404(Liga, id=liga_id, temporada=temporada_actual)
        else:
            liga_actual = ligas.first()

        # Guardar en el objeto para usar en get_context_data
        self.liga_actual = liga_actual
        self.ligas = ligas

        # Devolver queryset filtrado
        return Partido.objects.filter(
            liga=liga_actual
        ).order_by('jornada', 'fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Añadir ligas y liga actual al contexto
        context['ligas'] = getattr(self, 'ligas', [])
        context['liga_actual'] = getattr(self, 'liga_actual', None)

        # Si no hay liga seleccionada, no hay más contexto para añadir
        if not hasattr(self, 'liga_actual'):
            context['partidos_por_jornada'] = {}
            context['jornadas_ordenadas'] = []
            return context

        # Agrupar partidos por jornada
        partidos = self.get_queryset()
        partidos_por_jornada = {}

        for partido in partidos:
            if partido.jornada not in partidos_por_jornada:
                partidos_por_jornada[partido.jornada] = []
            partidos_por_jornada[partido.jornada].append(partido)

        # Ordenar jornadas
        jornadas_ordenadas = sorted(partidos_por_jornada.keys())

        # Añadir al contexto
        context['partidos_por_jornada'] = partidos_por_jornada
        context['jornadas_ordenadas'] = jornadas_ordenadas

        return context
