# Generated by Django 5.0.2 on 2024-03-19 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indexprice',
            name='date',
            field=models.DateField(),
        ),
    ]
