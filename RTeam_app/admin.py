from django.contrib import admin
from .models import (
    Temporada, Equipo, Jugador, JugadorEquipoTemporada,
    Entrenador, EntrenadorEquipoTemporada, Liga, EquipoLigaTemporada
)

# Register your models here.
admin.site.register(Temporada)
admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(JugadorEquipoTemporada)
admin.site.register(Entrenador)
admin.site.register(EntrenadorEquipoTemporada)
admin.site.register(Liga)
admin.site.register(EquipoLigaTemporada)
