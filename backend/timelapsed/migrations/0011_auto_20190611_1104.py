# Generated by Django 2.2.2 on 2019-06-11 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timelapsed', '0010_auto_20190611_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='date_range',
            name='Weeks_Skipped',
            field=models.IntegerField(),
        ),
    ]
