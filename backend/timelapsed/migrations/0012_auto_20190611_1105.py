# Generated by Django 2.2.2 on 2019-06-11 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timelapsed', '0011_auto_20190611_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='date_range',
            name='Begin_Date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='date_range',
            name='Day',
            field=models.TextField(max_length=100),
        ),
        migrations.AlterField(
            model_name='date_range',
            name='Num_Weeks',
            field=models.IntegerField(),
        ),
    ]