# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-09 12:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_auto_20161108_2255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('0', 'Reporter needs to approve'), ('1', 'Queried by reporter'), ('2', 'Approved by reporter'), ('3', 'Approved by editor'), ('4', 'Paid')], default='0', max_length=2),
        ),
    ]