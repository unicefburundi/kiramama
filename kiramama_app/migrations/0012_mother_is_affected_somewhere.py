# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-12-18 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kiramama_app', '0011_reportrec'),
    ]

    operations = [
        migrations.AddField(
            model_name='mother',
            name='is_affected_somewhere',
            field=models.BooleanField(default=True),
        ),
    ]