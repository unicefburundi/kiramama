# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-11 10:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [("kiramama_app", "0017_settings_setting_code")]

    operations = [
        migrations.AddField(
            model_name="chw",
            name="reg_date",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(2017, 1, 11, 10, 0, 41, 657000, tzinfo=utc),
            ),
            preserve_default=False,
        )
    ]
