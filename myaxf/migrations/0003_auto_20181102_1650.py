# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-02 08:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myaxf', '0002_nav'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='nav',
            table='axf_nav',
        ),
    ]