# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 18:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LabModule', '0007_auto_20170316_1240'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maquinaprofile',
            options={'permissions': (('can_addMachine', 'maquina||agregar'), ('can_edditMachine', 'maquina||editar')), 'verbose_name': 'M\xe1quina', 'verbose_name_plural': 'M\xe1quinas'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'Usuario', 'verbose_name_plural': 'Usuarios'},
        ),
        migrations.AddField(
            model_name='maquinaprofile',
            name='activa',
            field=models.BooleanField(default=True, verbose_name='Activa'),
        ),
        migrations.AddField(
            model_name='maquinaprofile',
            name='con_reserva',
            field=models.BooleanField(default=True, verbose_name='Reservable'),
        ),
    ]