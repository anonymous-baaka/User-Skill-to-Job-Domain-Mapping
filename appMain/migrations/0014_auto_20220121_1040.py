# Generated by Django 3.1.7 on 2022-01-21 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appMain', '0013_tech_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='soft_question',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=200)),
                ('option1', models.CharField(max_length=150)),
                ('option2', models.CharField(max_length=150)),
                ('option3', models.CharField(max_length=150)),
                ('option4', models.CharField(max_length=150)),
                ('answer', models.CharField(max_length=10)),
                ('tag', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='tech_question',
            name='option1',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='tech_question',
            name='option2',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='tech_question',
            name='option3',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='tech_question',
            name='option4',
            field=models.CharField(max_length=150),
        ),
    ]
