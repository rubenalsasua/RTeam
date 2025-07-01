from django import forms
from .models import Temporada, Equipo, Jugador, Entrenador


class TemporadaForm(forms.ModelForm):
    class Meta:
        model = Temporada
        fields = ['periodo', 'activa']
        widgets = {
            'periodo': forms.TextInput(attrs={'placeholder': 'YYYY/YYYY', 'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'periodo': 'Periodo',
            'activa': '¿Es la temporada actual?',
        }
        help_texts = {
            'periodo': 'Formato: YYYY/YYYY (ej: 2024/2025)',
        }
