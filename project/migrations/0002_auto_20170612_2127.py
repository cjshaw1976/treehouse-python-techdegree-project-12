# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-12 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectposition',
            name='quantity',
        ),
        migrations.AddField(
            model_name='project',
            name='requirements',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='project',
            name='timeline',
            field=models.TextField(default=''),
        ),
    ]
