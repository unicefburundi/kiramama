# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-05-14 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kiramama_app', '0027_auto_20180513_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='vac',
            name='received_after_how_many_weeks',
            field=models.CharField(max_length=10, null=True),
        ),
    ]