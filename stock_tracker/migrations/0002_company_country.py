# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-26 21:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='country',
            field=models.CharField(default='Nothing', max_length=200),
            preserve_default=False,
        ),
    ]
