# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-05-13 08:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kiramama_app", "0026_reportris_mother_arrived_at_health_facility")
    ]

    operations = [
        migrations.AlterField(
            model_name="reportcon",
            name="next_appointment_date",
            field=models.DateField(null=True),
        )
    ]
