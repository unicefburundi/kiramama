# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-06 18:20
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [("kiramama_app", "0008_auto_20161106_1141")]

    operations = [
        migrations.AddField(
            model_name="notificationschw",
            name="date_time_for_sending",
            field=models.DateTimeField(
                default=datetime.datetime(2016, 11, 6, 18, 20, 12, 206776, tzinfo=utc)
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notificationsmother",
            name="date_time_for_sending",
            field=models.DateTimeField(
                default=datetime.datetime(2016, 11, 6, 18, 20, 22, 52403, tzinfo=utc)
            ),
            preserve_default=False,
        ),
    ]
