# Generated by Django 5.2.3 on 2025-07-31 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RTeam_app', '0014_partido_eventopartido_convocatoriapartido'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='color',
            field=models.CharField(blank=True, help_text='Color principal del equipo', max_length=20, null=True),
        ),
    ]
