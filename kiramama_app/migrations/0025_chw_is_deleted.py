# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-12-18 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kiramama_app', '0024_provincesupervisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='chw',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]