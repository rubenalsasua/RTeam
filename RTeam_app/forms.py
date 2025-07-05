from django import forms
from .models import Temporada, Liga, Equipo, Jugador, Entrenador


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
        fields = ['nombre', 'temporada']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la liga', 'class': 'form-control'}),
            'temporada': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre de la Liga',
            'temporada': 'Temporada',
        }

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del equipo', 'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'nombre': 'Nombre del Equipo',
            'foto': 'Foto del Equipo',
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