# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-04-09 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("kiramama_app", "0025_chw_is_deleted")]

    operations = [
        migrations.AddField(
            model_name="reportris",
            name="mother_arrived_at_health_facility",
            field=models.BooleanField(default=False),
        )
    ]
