# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-04 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kiramama_app', '0016_chw_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='setting_code',
            field=models.CharField(default='CHWAI', max_length=20),
            preserve_default=False,
        ),
    ]