# Generated by Django 4.0.5 on 2022-09-12 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cargoloading', '0006_cargo_alter_cargolist_height_alter_cargolist_length_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargolist',
            name='cargo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cargoloading.cargo'),
        ),
    ]
