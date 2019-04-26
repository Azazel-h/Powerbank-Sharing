# Generated by Django 2.1.3 on 2019-04-06 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sharing', '0002_auto_20190406_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='powerbank',
            name='is_held',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='hold',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sharing.Powerbank'),
        ),
    ]