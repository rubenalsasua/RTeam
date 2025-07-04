# Generated by Django 5.2.3 on 2025-06-30 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RTeam_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jugadorequipotemporada',
            old_name='dorsal_en_temporada',
            new_name='dorsal',
        ),
        migrations.RemoveField(
            model_name='jugador',
            name='asistencias',
        ),
        migrations.RemoveField(
            model_name='jugador',
            name='dorsal',
        ),
        migrations.RemoveField(
            model_name='jugador',
            name='goles',
        ),
        migrations.RemoveField(
            model_name='jugador',
            name='tarjetas_amarillas',
        ),
        migrations.RemoveField(
            model_name='jugador',
            name='tarjetas_rojas',
        ),
        migrations.AddField(
            model_name='jugadorequipotemporada',
            name='asistencias',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='jugadorequipotemporada',
            name='goles',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='jugadorequipotemporada',
            name='tarjetas_amarillas',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='jugadorequipotemporada',
            name='tarjetas_rojas',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
