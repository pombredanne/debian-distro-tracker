# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-07 17:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_longer_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='uri',
            field=models.CharField(max_length=200, verbose_name='URI'),
        ),
    ]