# Generated by Django 5.2.3 on 2025-07-05 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RTeam_app', '0004_remove_entrenador_tipo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='temporada',
            name='activa',
        ),
    ]
