# Generated by Django 4.0.5 on 2022-09-12 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cargoloading', '0007_cargolist_cargo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cargo',
            name='csvFile',
        ),
    ]
