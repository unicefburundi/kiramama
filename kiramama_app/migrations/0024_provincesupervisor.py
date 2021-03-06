# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-12-11 12:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("public_administration_structure_app", "0001_initial"),
        ("kiramama_app", "0023_symptom_kirundi_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProvinceSupervisor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "province",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="public_administration_structure_app.Province",
                    ),
                ),
                (
                    "supervisor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="kiramama_app.AllSupervisor",
                    ),
                ),
            ],
        )
    ]
