from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
import re


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sign_up_method = models.CharField(max_length=20, default='google')
    full_name = models.CharField(max_length=255, blank=True)  # Campo para nombre completo
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('JUGADOR', 'Jugador'),
        ('INVITADO', 'Invitado'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='INVITADO')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class TemporadaField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 9
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if not re.match(r'^\d{4}/\d{4}$', value):
            raise ValidationError('El formato debe ser YYYY/YYYY (ej: 2024/2025)')

        año_inicio, año_fin = map(int, value.split('/'))
        if año_fin != año_inicio + 1:
            raise ValidationError('La temporada debe cubrir años consecutivos')


class Temporada(models.Model):
    periodo = TemporadaField(help_text='Formato: YYYY/YYYY (ej: 2024/2025)')

    class Meta:
        verbose_name_plural = "Temporadas"

    def __str__(self):
        return self.periodo


class Equipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    foto = models.ImageField(upload_to='equipos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    jugadores = models.ManyToManyField('Jugador', through='JugadorEquipoTemporada', related_name='equipos')
    entrenadores = models.ManyToManyField('Entrenador', through='EntrenadorEquipoTemporada', related_name='equipos')

    class Meta:
        verbose_name_plural = "Equipos"

    def __str__(self):
        return self.nombre


class Jugador(models.Model):
    nombre = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='jugadores/', null=True, blank=True)
    POSICIONES = [
        ('PORTERO', 'Portero'),
        ('CIERRE', 'Cierre'),
        ('ALA', 'Ala'),
        ('PIVOT', 'Pívot'),
    ]
    posicion = models.CharField(max_length=10, choices=POSICIONES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Jugadores"

    def __str__(self):
        return self.nombre


class JugadorEquipoTemporada(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    dorsal = models.PositiveIntegerField(default=0)
    fecha_incorporacion = models.DateField(auto_now_add=True)
    goles = models.PositiveIntegerField(default=0)
    asistencias = models.PositiveIntegerField(default=0)
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    tarjetas_rojas = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('jugador', 'equipo', 'temporada')
        verbose_name = "Jugador en Equipo por Temporada"
        verbose_name_plural = "Jugadores en Equipos por Temporada"

    def __str__(self):
        return f"{self.jugador} - {self.equipo} ({self.temporada})"


class Entrenador(models.Model):
    nombre = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='entrenadores/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Entrenadores"

    def __str__(self):
        return self.nombre


class EntrenadorEquipoTemporada(models.Model):
    entrenador = models.ForeignKey(Entrenador, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    TIPO = [
        ('ENTRENADOR', 'Entrenador'),
        ('DELEGADO', 'Delegado'),
        ('ENTRENADOR_PRACTICAS', 'Entrenador en Prácticas'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO, default='PRINCIPAL')
    fecha_incorporacion = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('entrenador', 'equipo', 'temporada')
        verbose_name = "Entrenador en Equipo por Temporada"
        verbose_name_plural = "Entrenadores en Equipos por Temporada"

    def __str__(self):
        return f"{self.entrenador} - {self.equipo} ({self.temporada})"


class Liga(models.Model):
    nombre = models.CharField(max_length=100)
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    equipos = models.ManyToManyField('Equipo', through='EquipoLigaTemporada', related_name='ligas')

    class Meta:
        unique_together = ('nombre', 'temporada')
        verbose_name_plural = "Ligas"

    def __str__(self):
        return f"{self.nombre} ({self.temporada})"


class EquipoLigaTemporada(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE)
    fecha_incorporacion = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('equipo', 'liga')
        verbose_name = "Equipo en Liga"
        verbose_name_plural = "Equipos en Ligas"

    def __str__(self):
        return f"{self.equipo} - {self.liga}"
