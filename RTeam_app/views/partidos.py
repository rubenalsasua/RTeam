from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import PartidoForm, ConvocatoriaForm
from RTeam_app.models import Liga, Partido, Temporada, Equipo, ConvocatoriaPartido, Jugador, \
    JugadorEquipoTemporada
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import json


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
    convocatoria = ConvocatoriaPartido.objects.filter(
        partido=partido,
        equipo=equipo
    ).select_related('jugador').order_by('estado', 'dorsal')

    # Generar imagen
    formato = request.GET.get('formato', 'jpeg')  # Cambiado de 'jpg' a 'jpeg'

    # Asegurar que el formato es correcto para PIL
    if formato.lower() == 'jpg':
        formato = 'jpeg'

    img_io = generar_imagen_convocatoria(partido, equipo, convocatoria, formato)

    # Determinar la extensión correcta para el nombre de archivo
    extension = 'jpg' if formato.lower() == 'jpeg' else formato.lower()

    # Devolver como descarga
    response = HttpResponse(img_io.getvalue(), content_type=f'image/{formato.lower()}')
    response['Content-Disposition'] = f'attachment; filename="convocatoria_{partido.id}_{equipo.id}.{extension}"'
    return response


def generar_imagen_convocatoria(partido, equipo, convocatoria, formato='jpeg'):
    """Genera una imagen con la convocatoria del equipo"""
    # [resto del código permanece igual]
    # Configuración básica de la imagen
    width, height = 1080, 1920  # Tamaño para móvil
    bg_color = (25, 25, 25)  # Fondo oscuro

    # Crear imagen y contexto de dibujo
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Cargar fuentes
    try:
        titulo_font = ImageFont.truetype("arial.ttf", 60)
        subtitulo_font = ImageFont.truetype("arial.ttf", 40)
        nombre_font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        # Usar fuente por defecto si no encuentra arial
        titulo_font = ImageFont.load_default()
        subtitulo_font = ImageFont.load_default()
        nombre_font = ImageFont.load_default()

    # Color del equipo
    equipo_color = equipo.color or "#ffaa00"
    equipo_rgb = tuple(int(equipo_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

    # Cabecera con degradado
    for y in range(200):
        # Degradado desde el color del equipo hasta transparente
        alpha = 255 - int(y * 1.2)
        if alpha < 0:
            alpha = 0
        color = equipo_rgb + (alpha,)
        draw.rectangle([(0, y), (width, y)], fill=color)

    # Título y subtítulo
    draw.text((width // 2, 100), "CONVOCATORIA", fill=(255, 255, 255), font=titulo_font, anchor="mm")
    draw.text((width // 2, 170), f"{equipo.nombre}", fill=equipo_rgb, font=subtitulo_font, anchor="mm")

    # Información del partido
    partido_text = f"{partido.equipo_local.nombre} vs {partido.equipo_visitante.nombre}"
    fecha_text = partido.fecha.strftime("%d/%m/%Y %H:%M")
    draw.text((width // 2, 250), partido_text, fill=(255, 255, 255), font=subtitulo_font, anchor="mm")
    draw.text((width // 2, 300), fecha_text, fill=(200, 200, 200), font=nombre_font, anchor="mm")

    # Logo del equipo (si existe)
    if equipo.foto:
        try:
            # Cargar logo del equipo
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            from io import BytesIO
            import requests

            # Obtener la imagen
            response = requests.get(equipo.foto.url)
            logo = Image.open(BytesIO(response.content))

            # Redimensionar logo
            logo_width = 200
            logo_height = int(logo.height * logo_width / logo.width)
            logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

            # Calcular posición para centrar
            logo_x = (width - logo_width) // 2
            logo_y = 350

            # Crear máscara para transparencia
            mask = Image.new('L', logo.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rectangle((0, 0, logo_width, logo_height), fill=255)

            # Pegar logo con transparencia
            img.paste(logo, (logo_x, logo_y), mask=mask)

        except Exception as e:
            print(f"Error al cargar logo: {e}")

    # Dibujar jugadores convocados
    y_pos = 500

    # Jugadores convocados
    draw.text((width // 2, y_pos), "JUGADORES CONVOCADOS", fill=equipo_rgb, font=subtitulo_font, anchor="mm")
    y_pos += 70

    convocados = [c for c in convocatoria if c.estado == 'CONVOCADO']
    no_convocados = [c for c in convocatoria if c.estado != 'CONVOCADO']

    for convocado in convocados:
        # Dorsal en círculo
        dorsal_x = 100
        dorsal_y = y_pos + 15
        dorsal_radius = 30

        draw.ellipse(
            [(dorsal_x - dorsal_radius, dorsal_y - dorsal_radius),
             (dorsal_x + dorsal_radius, dorsal_y + dorsal_radius)],
            fill=equipo_rgb
        )

        # Número del dorsal
        dorsal_texto = str(convocado.dorsal or "")
        draw.text((dorsal_x, dorsal_y), dorsal_texto, fill=(255, 255, 255),
                  font=nombre_font, anchor="mm")

        # Nombre del jugador
        nombre_x = dorsal_x + dorsal_radius + 30
        draw.text((nombre_x, dorsal_y), convocado.jugador.nombre,
                  fill=(255, 255, 255), font=nombre_font, anchor="lm")

        # Posición del jugador
        posicion_x = width - 100
        draw.text((posicion_x, dorsal_y), convocado.jugador.get_posicion_display(),
                  fill=(200, 200, 200), font=nombre_font, anchor="rm")

        y_pos += 70

    # Si hay no convocados, mostrarlos separados
    if no_convocados:
        y_pos += 30
        draw.text((width // 2, y_pos), "NO CONVOCADOS", fill=(180, 180, 180),
                  font=subtitulo_font, anchor="mm")
        y_pos += 70

        for no_convocado in no_convocados:
            estado = no_convocado.get_estado_display()
            draw.text((100, y_pos), f"{no_convocado.jugador.nombre} ({estado})",
                      fill=(150, 150, 150), font=nombre_font, anchor="lm")
            y_pos += 50

    # Pie de imagen
    draw.text((width // 2, height - 100), "RTeam", fill=(120, 120, 120),
              font=nombre_font, anchor="mm")

    # Guardar la imagen en memoria
    img_io = BytesIO()
    # Asegurarse de que el formato es correcto para PIL
    format_pil = formato.upper()
    if format_pil == 'JPG':
        format_pil = 'JPEG'

    img.save(img_io, format=format_pil, quality=90)
    img_io.seek(0)

    return img_io
