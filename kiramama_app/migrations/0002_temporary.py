# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-22 10:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('health_administration_structure_app', '0001_initial'),
        ('public_administration_structure_app', '0001_initial'),
        ('kiramama_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temporary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20)),
                ('supervisor_phone_number', models.CharField(max_length=20)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='health_administration_structure_app.CDS')),
                ('sub_hill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='public_administration_structure_app.SousColline')),
            ],
        ),
    ]