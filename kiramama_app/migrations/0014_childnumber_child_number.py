# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-12-18 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kiramama_app', '0013_cpn_report_symptom'),
    ]

    operations = [
        migrations.AddField(
            model_name='childnumber',
            name='child_number',
            field=models.IntegerField(default=1),
        ),
    ]