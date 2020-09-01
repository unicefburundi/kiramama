# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2019-03-08 08:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kiramama_app', '0028_vac_received_after_how_many_weeks'),
    ]

    operations = [
        migrations.CreateModel(
            name='MicronutrientIntake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('micronutrient_intake_code', models.CharField(max_length=10)),
                ('micronutrient_intake_description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ReportDepistage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('depistage_date', models.DateField()),
                ('number_of_children_in_green', models.IntegerField()),
                ('number_of_children_in_yellow', models.IntegerField()),
                ('number_of_children_in_red', models.IntegerField()),
                ('number_of_children_with_oedem', models.IntegerField()),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.Report')),
            ],
        ),
        migrations.CreateModel(
            name='ReportMicroNTDistribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intake_date', models.DateField()),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.ReportNSC')),
                ('intake', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.MicronutrientIntake')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.Report')),
            ],
        ),
        migrations.CreateModel(
            name='ReportPriseC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pc_date', models.DateField()),
                ('muac', models.FloatField()),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.ReportNSC')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.Report')),
            ],
        ),
        migrations.CreateModel(
            name='ReportResponsePC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child_health_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.HealthStatus')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.Report')),
                ('report_prise_charge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.ReportPriseC')),
            ],
        ),
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_code', models.CharField(max_length=50)),
                ('time_code_description', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='rescue',
            name='rescue_description',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='reportprisec',
            name='rescue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.Rescue'),
        ),
        migrations.AddField(
            model_name='reportprisec',
            name='rescuered_when',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.Time'),
        ),
        migrations.AddField(
            model_name='reportprisec',
            name='symptom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiramama_app.Symptom'),
        ),
    ]