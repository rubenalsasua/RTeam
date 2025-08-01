# Generated by Django 5.2.3 on 2025-07-27 15:50

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RTeam_app', '0012_alter_entrenadorequipotemporada_tipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('ubicacion', models.CharField(blank=True, max_length=255, null=True)),
                ('foto', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='imagen')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Campos',
            },
        ),
    ]
