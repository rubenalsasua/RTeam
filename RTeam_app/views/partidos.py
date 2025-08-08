from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import PartidoForm, ConvocatoriaForm, EventoPartidoForm
from RTeam_app.models import Liga, Partido, Temporada, Equipo, ConvocatoriaPartido, Jugador, \
    JugadorEquipoTemporada, Campo, EventoPartido
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import json
import imgkit
import os
from django.template.loader import render_to_string


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
            liga_destacada = ligas.filter(destacada=True).first()
            liga_actual = liga_destacada if liga_destacada else ligas.first()

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


# RTeam_app/views/partidos.py
class PartidoCreateView(LoginRequiredMixin, CreateView):
    model = Partido
    form_class = PartidoForm
    template_name = 'partidos/partido_create.html'

    def get_success_url(self):
        return reverse_lazy('partido_list') + f'?liga={self.kwargs["liga_id"]}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        liga = get_object_or_404(Liga, id=self.kwargs['liga_id'])
        context['liga'] = liga
        context['accion'] = 'Crear'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        liga = get_object_or_404(Liga, id=self.kwargs['liga_id'])
        equipos_liga = Equipo.objects.filter(ligas=liga)
        form.fields['equipo_local'].queryset = equipos_liga
        form.fields['equipo_visitante'].queryset = equipos_liga
        form.initial['estado'] = 'PROGRAMADO'
        return form

    def form_valid(self, form):
        liga = get_object_or_404(Liga, id=self.kwargs['liga_id'])
        form.instance.liga = liga
        return super().form_valid(form)


# RTeam_app/views/partidos.py - Modificación del método get_context_data de PartidoDetailView

class PartidoDetailView(LoginRequiredMixin, DetailView):
    model = Partido
    template_name = 'partidos/partido_detail.html'
    context_object_name = 'partido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partido = self.object

        # Obtener convocatorias para equipo local y visitante
        context['convocatoria_local'] = ConvocatoriaPartido.objects.filter(
            partido=partido, equipo=partido.equipo_local
        ).select_related('jugador').order_by('dorsal')

        context['convocatoria_visitante'] = ConvocatoriaPartido.objects.filter(
            partido=partido, equipo=partido.equipo_visitante
        ).select_related('jugador').order_by('dorsal')

        # Agregar eventos y goles
        eventos = EventoPartido.objects.filter(partido=partido).select_related('jugador', 'asistidor')
        context['eventos'] = eventos

        goles_local = eventos.filter(
            tipo_evento='GOL',
            jugador__in=ConvocatoriaPartido.objects.filter(
                partido=partido,
                equipo=partido.equipo_local
            ).values_list('jugador', flat=True)
        ).count()

        goles_visitante = eventos.filter(
            tipo_evento='GOL',
            jugador__in=ConvocatoriaPartido.objects.filter(
                partido=partido,
                equipo=partido.equipo_visitante
            ).values_list('jugador', flat=True)
        ).count()

        context['goles_local'] = goles_local
        context['goles_visitante'] = goles_visitante

        return context


class EntrenadorAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.profile.role in ['ADMIN', 'ENTRENADOR']


class ConvocatoriaListView(LoginRequiredMixin, EntrenadorAdminRequiredMixin, ListView):
    model = ConvocatoriaPartido
    template_name = 'partidos/partido_convocatoria_list.html'

    def get_queryset(self):
        self.partido = get_object_or_404(Partido, pk=self.kwargs['partido_id'])
        self.equipo_id = self.kwargs['equipo_id']
        return ConvocatoriaPartido.objects.filter(
            partido=self.partido,
            equipo_id=self.equipo_id
        ).select_related('jugador')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partido'] = self.partido
        context['equipo'] = self.partido.equipo_local if self.partido.equipo_local.id == int(
            self.equipo_id) else self.partido.equipo_visitante
        return context


class ConvocatoriaCreateView(LoginRequiredMixin, EntrenadorAdminRequiredMixin, CreateView):
    model = ConvocatoriaPartido
    form_class = ConvocatoriaForm
    template_name = 'partidos/partido_convocatoria_create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        partido = get_object_or_404(Partido, pk=self.kwargs['partido_id'])
        equipo_id = self.kwargs['equipo_id']
        temporada = partido.liga.temporada

        # Obtener jugadores ya convocados (para excluirlos)
        jugadores_ya_convocados = ConvocatoriaPartido.objects.filter(
            partido=partido,
            equipo_id=equipo_id
        ).values_list('jugador_id', flat=True)

        # Filtrar jugadores que pertenecen al equipo en la temporada actual
        # y que no están ya convocados
        jugadores_equipo = JugadorEquipoTemporada.objects.filter(
            equipo_id=equipo_id,
            temporada=temporada
        ).exclude(jugador_id__in=jugadores_ya_convocados)

        # Crear un diccionario con los dorsales de cada jugador
        dorsales = {jet.jugador_id: jet.dorsal for jet in jugadores_equipo}

        # Ajustar el queryset para mostrar solo los jugadores disponibles
        form.fields['jugador'].queryset = Jugador.objects.filter(
            id__in=jugadores_equipo.values_list('jugador_id', flat=True)
        )

        # Añadir JavaScript para cambiar el dorsal automáticamente
        form.fields['jugador'].widget.attrs.update({
            'onchange': 'actualizarDorsal(this.value)',
            'data-dorsales': json.dumps(dorsales)
        })

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partido = get_object_or_404(Partido, pk=self.kwargs['partido_id'])
        equipo_id = self.kwargs['equipo_id']
        context['partido'] = partido

        # Verificar si el equipo es local o visitante
        if partido.equipo_local.id == int(equipo_id):
            context['equipo'] = partido.equipo_local
        elif partido.equipo_visitante.id == int(equipo_id):
            context['equipo'] = partido.equipo_visitante
        else:
            context['equipo'] = get_object_or_404(Equipo, id=equipo_id)

        return context

    def form_valid(self, form):
        form.instance.partido_id = self.kwargs['partido_id']
        form.instance.equipo_id = self.kwargs['equipo_id']

        # Si el dorsal está vacío, obtenerlo de la temporada
        if not form.instance.dorsal:
            partido = get_object_or_404(Partido, pk=self.kwargs['partido_id'])
            temporada = partido.liga.temporada
            try:
                jet = JugadorEquipoTemporada.objects.get(
                    jugador=form.instance.jugador,
                    equipo_id=self.kwargs['equipo_id'],
                    temporada=temporada
                )
                form.instance.dorsal = jet.dorsal
            except JugadorEquipoTemporada.DoesNotExist:
                form.instance.dorsal = 0  # Valor por defecto si no tiene dorsal asignado

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('convocatoria_list',
                            kwargs={'partido_id': self.kwargs['partido_id'],
                                    'equipo_id': self.kwargs['equipo_id']})


class ConvocatoriaDeleteView(LoginRequiredMixin, EntrenadorAdminRequiredMixin, DeleteView):
    model = ConvocatoriaPartido
    template_name = 'partidos/partido_convocatoria_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('convocatoria_list', kwargs={
            'partido_id': self.object.partido.id,
            'equipo_id': self.object.equipo.id
        })


def exportar_convocatoria(request, partido_id, equipo_id):
    """Exportar la convocatoria a una imagen (JPEG/PNG)"""
    partido = get_object_or_404(Partido, pk=partido_id)
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    campo = get_object_or_404(Campo, pk=partido.campo_id)
    convocatoria = ConvocatoriaPartido.objects.filter(
        partido=partido,
        equipo=equipo
    ).select_related('jugador').order_by('estado', 'dorsal')
    entrenadores = equipo.entrenadores.all()

    # Separar convocados y no convocados
    convocados = [c for c in convocatoria if c.estado == 'CONVOCADO']
    no_convocados = [c for c in convocatoria if c.estado != 'CONVOCADO']

    # Color del equipo
    equipo_color = equipo.color or "#ffaa00"
    # Crear una versión rgba para el gradiente
    r = int(equipo_color.lstrip('#')[0:2], 16)
    g = int(equipo_color.lstrip('#')[2:4], 16)
    b = int(equipo_color.lstrip('#')[4:6], 16)
    equipo_color_rgba = f"rgba({r},{g},{b},0.8)"

    # Generar el HTML
    html_content = render_to_string('partidos/convocatoria_export.html', {
        'partido': partido,
        'equipo': equipo,
        'convocados': convocados,
        'no_convocados': no_convocados,
        'equipo_color': equipo_color,
        'equipo_color_rgba': equipo_color_rgba,
        'entrenadores': entrenadores,
        'campo': campo,
    })

    # Determinar el formato
    formato = request.GET.get('formato', 'jpeg')
    if formato.lower() == 'jpg':
        formato = 'jpeg'

    # Convertir HTML a imagen
    img_data = html_to_image(html_content, formato)

    # Determinar la extensión correcta para el nombre de archivo
    extension = 'jpg' if formato.lower() == 'jpeg' else formato.lower()

    # Devolver como descarga
    response = HttpResponse(img_data, content_type=f'image/{formato.lower()}')
    response[
        'Content-Disposition'] = f'attachment; filename="Convocatoria_{partido.equipo_local}_{partido.equipo_visitante}_{partido.fecha}.{extension}"'
    return response


def html_to_image(html_content, formato='jpeg'):
    options = {
        'format': formato,
        'width': 1080,
        'height': 1920,
        'quality': 90,
        'enable-local-file-access': None
    }

    # Especifica la ruta completa a wkhtmltoimage según tu sistema
    wkhtmltoimage_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'  # Ajusta esta ruta

    if 'PYTHONANYWHERE_DOMAIN' in os.environ:
        wkhtmltoimage_path = '/usr/bin/wkhtmltoimage'

    config = imgkit.config(wkhtmltoimage=wkhtmltoimage_path)
    img_data = imgkit.from_string(html_content, False, options=options, config=config)
    return img_data


class EventoCreateView(LoginRequiredMixin, CreateView):
    model = EventoPartido
    form_class = EventoPartidoForm
    template_name = 'partidos/evento_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        partido = get_object_or_404(Partido, pk=self.kwargs['partido_id'])
        kwargs['partido'] = partido
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partido'] = get_object_or_404(Partido, pk=self.kwargs['partido_id'])
        return context

    def form_valid(self, form):
        partido = get_object_or_404(Partido, pk=self.kwargs['partido_id'])
        form.instance.partido = partido
        response = super().form_valid(form)

        if partido.estado != 'FINALIZADO':
            partido.estado = 'FINALIZADO'
            partido.save()
        return response

    def get_success_url(self):
        return reverse_lazy('partido_detail', kwargs={'pk': self.kwargs['partido_id']})


class EventoDeleteView(LoginRequiredMixin, DeleteView):
    model = EventoPartido
    template_name = 'partidos/evento_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('partido_detail', kwargs={'pk': self.object.partido.id})
