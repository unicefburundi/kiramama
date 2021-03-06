# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-17 13:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BPS",
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
                    "name",
                    models.CharField(max_length=20, unique=True, verbose_name="name"),
                ),
                ("code", models.IntegerField(blank=True, null=True, unique=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="CDS",
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
                ("name", models.CharField(max_length=40)),
                ("code", models.CharField(max_length=6, unique=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Pub", "Public"),
                            ("Con", "Conf"),
                            ("Priv", "Prive"),
                            ("Ass", "Ass"),
                            ("HPub", "HPublic"),
                            ("HCon", "HConf"),
                            ("HPrv", "HPrive"),
                        ],
                        help_text="Either Public, Conf, Ass, Prive  or Hospital status.",
                        max_length=4,
                        null=True,
                    ),
                ),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="District",
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
                    "name",
                    models.CharField(max_length=40, unique=True, verbose_name="nom"),
                ),
                ("code", models.IntegerField(unique=True)),
                (
                    "bps",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="health_administration_structure_app.BPS",
                        verbose_name="BPS",
                    ),
                ),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.AddField(
            model_name="cds",
            name="district",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="health_administration_structure_app.District",
            ),
        ),
    ]
