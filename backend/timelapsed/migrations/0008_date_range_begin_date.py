# Generated by Django 2.1.7 on 2019-04-25 02:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('timelapsed', '0007_auto_20190424_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='date_range',
            name='Begin_Date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
