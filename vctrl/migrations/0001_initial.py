# Generated by Django 3.0.7 on 2020-06-20 23:16

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='default', max_length=200)),
                ('dir', models.CharField(default='.', max_length=200)),
                ('description', models.CharField(default='The default scenario that BSSM loads in the absence of a regular scenario.ini file', max_length=200)),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=3600), verbose_name='Scenario time limit, in hours')),
                ('start', models.DateTimeField(default=datetime.datetime(2020, 6, 20, 23, 16, 24, 281576))),
            ],
        ),
        migrations.CreateModel(
            name='VM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=64)),
                ('in_scope', models.BooleanField(default=True, verbose_name='Whether or not this VM is in scope for this challenge.')),
                ('revertible', models.BooleanField(default=True, verbose_name='Whether or not the student is allowed to revert this machine.')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vctrl.Scenario')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('kali', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vctrl.VM')),
            ],
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('captured', models.BooleanField(default=False, verbose_name='Whether or not the student has found this flag.')),
                ('vm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vctrl.VM')),
            ],
        ),
    ]
