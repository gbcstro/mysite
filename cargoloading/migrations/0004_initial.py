# Generated by Django 4.0.5 on 2022-09-12 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cargoloading', '0003_delete_cargotable'),
    ]

    operations = [
        migrations.CreateModel(
            name='cargoList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('height', models.FloatField()),
                ('length', models.FloatField()),
                ('width', models.FloatField()),
                ('weight', models.FloatField()),
            ],
        ),
    ]