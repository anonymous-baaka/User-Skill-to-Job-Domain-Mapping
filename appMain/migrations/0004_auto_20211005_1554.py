# Generated by Django 3.2.7 on 2021-10-05 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appMain', '0003_auto_20211004_0056'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Student',
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]