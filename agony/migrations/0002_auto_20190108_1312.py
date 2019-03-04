# Generated by Django 2.1.4 on 2019-01-08 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0002_auto_20190107_0721'),
        ('agony', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='qanda',
            options={'ordering': ['-published'], 'verbose_name': 'Question and Answer', 'verbose_name_plural': 'Questions and Answers'},
        ),
        migrations.AddField(
            model_name='qanda',
            name='notify_sender',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='qanda',
            name='topics',
            field=models.ManyToManyField(blank=True, to='newsroom.Topic'),
        ),
    ]