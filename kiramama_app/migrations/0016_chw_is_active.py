# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-04 13:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kiramama_app', '0015_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='chw',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]