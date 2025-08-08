from django import forms
from .models import Temporada, Liga, Equipo, Jugador, Entrenador, EquipoLigaTemporada, JugadorEquipoTemporada, \
    EntrenadorEquipoTemporada, Profile, Partido, ConvocatoriaPartido, Campo, EventoPartido


class TemporadaForm(forms.ModelForm):
    class Meta:
        model = Temporada
        fields = ['periodo']
        widgets = {
            'periodo': forms.TextInput(attrs={'placeholder': 'YYYY/YYYY', 'class': 'form-control'}),
        }
        labels = {
            'periodo': 'Periodo',
        }
        help_texts = {
            'periodo': 'Formato: YYYY/YYYY (ej: 2024/2025)',
        }


class LigaForm(forms.ModelForm):
    class Meta:
        model = Liga
        fields = ['nombre', 'foto', 'color', 'temporada', 'destacada']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la liga', 'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'temporada': forms.Select(attrs={'class': 'form-control'}),
            'destacada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre de la Liga',
            'foto': 'Foto de la Liga',
            'color': 'Color de la Liga',
            'temporada': 'Temporada',
            'destacada': 'Liga destacada',
        }
        help_texts = {
            'destacada': 'Si se marca, esta liga aparecerá seleccionada por defecto en el listado de partidos',
        }


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'foto', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del equipo', 'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre del Equipo',
            'foto': 'Foto del Equipo',
            'color': 'Color del Equipo',
        }


class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['nombre', 'foto', 'posicion']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del jugador', 'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'posicion': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre del Jugador',
            'foto': 'Foto del Jugador',
            'posicion': 'Posición',
        }


class EntrenadorForm(forms.ModelForm):
    class Meta:
        model = Entrenador
        fields = ['nombre', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del entrenador', 'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'nombre': 'Nombre del Entrenador',
            'foto': 'Foto del Entrenador',
        }


class EquipoLigaTemporadaForm(forms.ModelForm):
    equipo = forms.ModelChoiceField(
        queryset=Equipo.objects.all(),
        label="Equipo"
    )

    class Meta:
        model = EquipoLigaTemporada
        fields = ['equipo']


class JugadorEquipoTemporadaForm(forms.ModelForm):
    jugador = forms.ModelChoiceField(
        queryset=Jugador.objects.all(),
        label="Jugador"
    )
    temporada = forms.ModelChoiceField(
        queryset=Temporada.objects.all(),
        label="Temporada"
    )

    class Meta:
        model = JugadorEquipoTemporada
        fields = ['jugador', 'temporada', 'dorsal']


class EntrenadorEquipoTemporadaForm(forms.ModelForm):
    entrenador = forms.ModelChoiceField(
        queryset=Entrenador.objects.all(),
        label="Entrenador"
    )
    temporada = forms.ModelChoiceField(
        queryset=Temporada.objects.all(),
        label="Temporada"
    )

    class Meta:
        model = EntrenadorEquipoTemporada
        fields = ['entrenador', 'temporada', 'tipo']


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'jugador', 'entrenador']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'jugador': forms.Select(attrs={'class': 'form-control'}),
            'entrenador': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'role': 'Rol',
            'jugador': 'Jugador asociado',
            'entrenador': 'Entrenador asociado'
        }
        help_texts = {
            'jugador': 'Selecciona un jugador para asociar a este perfil (opcional)',
            'entrenador': 'Selecciona un entrenador para asociar a este perfil (opcional)'
        }


class EventoPartidoForm(forms.ModelForm):
    class Meta:
        model = EventoPartido
        fields = ['jugador', 'tipo_evento', 'asistidor', 'descripcion']
        widgets = {
            'jugador': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'tipo_evento': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'asistidor': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'descripcion': forms.TextInput(
                attrs={'class': 'form-control form-control-sm', 'placeholder': 'Descripción opcional'}),
        }
        labels = {
            'jugador': 'Jugador',
            'tipo_evento': 'Tipo de Evento',
            'asistidor': 'Asistidor',
            'descripcion': 'Descripción',
        }

    def __init__(self, *args, partido=None, **kwargs):
        super().__init__(*args, **kwargs)
        if partido:
            # Obtener jugadores convocados de ambos equipos
            convocados_local = ConvocatoriaPartido.objects.filter(
                partido=partido,
                equipo=partido.equipo_local,
                estado='CONVOCADO'
            ).select_related('jugador')

            convocados_visitante = ConvocatoriaPartido.objects.filter(
                partido=partido,
                equipo=partido.equipo_visitante,
                estado='CONVOCADO'
            ).select_related('jugador')

            jugadores_ids = list(convocados_local.values_list('jugador_id', flat=True)) + \
                            list(convocados_visitante.values_list('jugador_id', flat=True))

            self.fields['jugador'].queryset = Jugador.objects.filter(id__in=jugadores_ids)
            self.fields['asistidor'].queryset = Jugador.objects.filter(id__in=jugadores_ids)
            self.fields['asistidor'].required = False


class PartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['fecha', 'jornada', 'campo', 'equipo_local', 'equipo_visitante']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
            'jornada': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
            'campo': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'equipo_local': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'equipo_visitante': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
        labels = {
            'fecha': 'Fecha y hora',
            'jornada': 'Jornada',
            'campo': 'Campo',
            'equipo_local': 'Equipo Local',
            'equipo_visitante': 'Equipo Visitante',
        }


class ConvocatoriaForm(forms.ModelForm):
    class Meta:
        model = ConvocatoriaPartido
        fields = ['jugador', 'estado', 'dorsal']
        widgets = {
            'jugador': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'estado': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'dorsal': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
        }
        labels = {
            'jugador': 'Jugador',
            'estado': 'Estado',
            'dorsal': 'Dorsal',
        }


class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = ['nombre', 'ubicacion', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del campo', 'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'placeholder': 'Ubicación del campo', 'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'nombre': 'Nombre del Campo',
            'ubicacion': 'Ubicación del Campo',
            'foto': 'Foto del Campo',
        }
