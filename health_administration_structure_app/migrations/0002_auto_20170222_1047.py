# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-02-22 08:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health_administration_structure_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bps',
            name='code',
            field=models.CharField(blank=True, max_length=2, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='cds',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='cds',
            name='status',
            field=models.CharField(blank=True, choices=[('Pub', 'Public'), ('Con', 'Conf'), ('Priv', 'Prive'), ('Ass', 'Ass'), ('HPub', 'HPublic'), ('HCon', 'HConf'), ('HPrv', 'HPrive')], help_text='Either Public, Conf, Ass, Prive  or Hospital status.', max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='district',
            name='code',
            field=models.CharField(max_length=4, unique=True),
        ),
    ]