from django import forms
from .models import Temporada, Liga, Equipo, Jugador, Entrenador, EquipoLigaTemporada, JugadorEquipoTemporada, \
    EntrenadorEquipoTemporada, Profile, Partido, ConvocatoriaPartido


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
