# Generated by Django 3.2.7 on 2021-10-14 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appMain', '0005_resume'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='pdf',
            field=models.FileField(upload_to='uploads/resume/'),
        ),
    ]