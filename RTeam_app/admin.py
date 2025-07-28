from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Profile, Temporada, Equipo, Jugador, JugadorEquipoTemporada, Campo,
    Entrenador, EntrenadorEquipoTemporada, Liga, EquipoLigaTemporada, Partido, EventoPartido, ConvocatoriaPartido
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'get_role')

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Profile.DoesNotExist:
            return '-'

    get_role.short_description = 'Rol'


# Reemplaza el UserAdmin predeterminado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register your models here.
admin.site.register(Temporada)
admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(JugadorEquipoTemporada)
admin.site.register(Entrenador)
admin.site.register(EntrenadorEquipoTemporada)
admin.site.register(Liga)
admin.site.register(EquipoLigaTemporada)
admin.site.register(Partido)
admin.site.register(EventoPartido)
admin.site.register(ConvocatoriaPartido)
admin.site.register(Campo)
