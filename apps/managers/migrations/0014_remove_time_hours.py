# Generated by Django 3.2.12 on 2022-04-04 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managers', '0013_auto_20220404_0728'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='time',
            name='hours',
        ),
    ]
