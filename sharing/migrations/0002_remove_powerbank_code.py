# Generated by Django 2.1.3 on 2019-05-11 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharing', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='powerbank',
            name='code',
        ),
    ]