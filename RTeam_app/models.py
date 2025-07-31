from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
import re
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from cloudinary import uploader
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sign_up_method = models.CharField(max_length=20, default='google')
    full_name = models.CharField(max_length=255, blank=True)
    last_visit = models.DateTimeField(null=True, blank=True)

    ROLES = [
        ('ADMIN', 'Administrador'),
        ('JUGADOR', 'Jugador'),
        ('ENTRENADOR', 'Entrenador'),
        ('INVITADO', 'Invitado'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='INVITADO')
    jugador = models.OneToOneField('Jugador', on_delete=models.SET_NULL, null=True, blank=True, related_name='profile')
    entrenador = models.OneToOneField('Entrenador', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='profile')

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
    foto = CloudinaryField('imagen', null=True, blank=True, folder='equipos')
    color = models.CharField(max_length=20, blank=True, null=True, help_text='Color principal del equipo')
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
    foto = CloudinaryField('imagen', null=True, blank=True, folder='jugadores')
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
    foto = CloudinaryField('imagen', null=True, blank=True, folder='entrenadores')
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
    tipo = models.CharField(max_length=20, choices=TIPO, default='ENTRENADOR')
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


@receiver(pre_delete, sender=Equipo)
def equipo_delete_handler(sender, instance, **kwargs):
    # Eliminar la imagen de Cloudinary si existe
    if instance.foto:
        # Extrae el public_id de la URL de Cloudinary
        try:
            # El public_id suele ser la parte final de la URL sin la extensión
            from urllib.parse import urlparse
            path = urlparse(instance.foto.url).path
            public_id = path.split('/')[-1].split('.')[0]
            uploader.destroy(public_id)
        except Exception as e:
            print(f"Error al eliminar imagen de Cloudinary: {e}")


@receiver(pre_delete, sender=Jugador)
def jugador_delete_handler(sender, instance, **kwargs):
    if instance.foto:
        try:
            from urllib.parse import urlparse
            path = urlparse(instance.foto.url).path
            public_id = path.split('/')[-1].split('.')[0]
            uploader.destroy(public_id)
        except Exception as e:
            print(f"Error al eliminar imagen de Cloudinary: {e}")


@receiver(pre_delete, sender=Entrenador)
def entrenador_delete_handler(sender, instance, **kwargs):
    if instance.foto:
        try:
            from urllib.parse import urlparse
            path = urlparse(instance.foto.url).path
            public_id = path.split('/')[-1].split('.')[0]
            uploader.destroy(public_id)
        except Exception as e:
            print(f"Error al eliminar imagen de Cloudinary: {e}")


@receiver(pre_save, sender=Equipo)
def equipo_update_handler(sender, instance, **kwargs):
    # Verificar si ya existe en la base de datos
    if instance.pk:
        try:
            # Obtener el objeto anterior
            anterior = Equipo.objects.get(pk=instance.pk)
            # Si la foto ha cambiado, eliminar la anterior
            if anterior.foto and anterior.foto != instance.foto:
                try:
                    from urllib.parse import urlparse
                    path = urlparse(anterior.foto.url).path
                    public_id = path.split('/')[-1].split('.')[0]
                    uploader.destroy(public_id)
                except Exception as e:
                    print(f"Error al eliminar imagen anterior: {e}")
        except Equipo.DoesNotExist:
            pass


@receiver(pre_save, sender=Jugador)
def jugador_update_handler(sender, instance, **kwargs):
    # Verificar si ya existe en la base de datos
    if instance.pk:
        try:
            # Obtener el objeto anterior
            anterior = Jugador.objects.get(pk=instance.pk)
            # Si la foto ha cambiado, eliminar la anterior
            if anterior.foto and anterior.foto != instance.foto:
                try:
                    from urllib.parse import urlparse
                    path = urlparse(anterior.foto.url).path
                    public_id = path.split('/')[-1].split('.')[0]
                    uploader.destroy(public_id)
                except Exception as e:
                    print(f"Error al eliminar imagen anterior: {e}")
        except Jugador.DoesNotExist:
            pass


@receiver(pre_save, sender=Entrenador)
def entrenador_update_handler(sender, instance, **kwargs):
    # Verificar si ya existe en la base de datos
    if instance.pk:
        try:
            # Obtener el objeto anterior
            anterior = Entrenador.objects.get(pk=instance.pk)
            # Si la foto ha cambiado, eliminar la anterior
            if anterior.foto and anterior.foto != instance.foto:
                try:
                    from urllib.parse import urlparse
                    path = urlparse(anterior.foto.url).path
                    public_id = path.split('/')[-1].split('.')[0]
                    uploader.destroy(public_id)
                except Exception as e:
                    print(f"Error al eliminar imagen anterior: {e}")
        except Entrenador.DoesNotExist:
            pass


class Campo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    foto = CloudinaryField('imagen', null=True, blank=True, folder='campos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Campos"

    def __str__(self):
        return self.nombre


@receiver(pre_delete, sender=Campo)
def campo_delete_handler(sender, instance, **kwargs):
    # Eliminar la imagen de Cloudinary si existe
    if instance.foto:
        try:
            from urllib.parse import urlparse
            path = urlparse(instance.foto.url).path
            public_id = path.split('/')[-1].split('.')[0]
            uploader.destroy(public_id)
        except Exception as e:
            print(f"Error al eliminar imagen de Cloudinary: {e}")


@receiver(pre_save, sender=Campo)
def campo_update_handler(sender, instance, **kwargs):
    # Verificar si ya existe en la base de datos
    if instance.pk:
        try:
            # Obtener el objeto anterior
            anterior = Campo.objects.get(pk=instance.pk)
            # Si la foto ha cambiado, eliminar la anterior
            if anterior.foto and anterior.foto != instance.foto:
                try:
                    from urllib.parse import urlparse
                    path = urlparse(anterior.foto.url).path
                    public_id = path.split('/')[-1].split('.')[0]
                    uploader.destroy(public_id)
                except Exception as e:
                    print(f"Error al eliminar imagen anterior: {e}")
        except Campo.DoesNotExist:
            pass


class Partido(models.Model):
    fecha = models.DateTimeField()
    jornada = models.PositiveIntegerField()
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE)
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_locales')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_visitantes')
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    ESTADO = [
        ('PROGRAMADO', 'Programado'),
        ('FINALIZADO', 'Finalizado'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Partidos"

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"


class EventoPartido(models.Model):
    TIPO = [
        ('GOL', 'Gol'),
        ('ASISTENCIA', 'Asistencia'),
        ('TARJETA_AMARILLA', 'Tarjeta Amarilla'),
        ('TARJETA_ROJA', 'Tarjeta Roja'),
    ]

    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='eventos_partido')
    asistidor = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='asistencias_partido')
    tipo_evento = models.CharField(max_length=20, choices=TIPO)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Eventos de Partido"

    def __str__(self):
        return f"{self.jugador} - {self.tipo_evento}"


class ConvocatoriaPartido(models.Model):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    ESTADOS = [
        ('CONVOCADO', 'Convocado'),
        ('NO_CONVOCADO', 'No Convocado'),
        ('LESIONADO', 'Lesionado'),
        ('SANCIONADO', 'Sancionado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CONVOCADO')
    dorsal = models.PositiveIntegerField(null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Convocatoria a Partido"
        verbose_name_plural = "Convocatorias a Partido"
        unique_together = ('partido', 'jugador')

    def __str__(self):
        return f"{self.jugador} - {self.partido} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        # Si no se especifica el dorsal, intentar obtenerlo de la relación JugadorEquipoTemporada
        if not self.dorsal:
            try:
                temporada = self.partido.liga.temporada
                jet = JugadorEquipoTemporada.objects.get(
                    jugador=self.jugador,
                    equipo=self.equipo,
                    temporada=temporada
                )
                self.dorsal = jet.dorsal
            except JugadorEquipoTemporada.DoesNotExist:
                pass
        super().save(*args, **kwargs)
