# Generated by Django 3.0 on 2020-09-30 16:42

import django.utils.timezone
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('tesla_ce', '0010_auto_20200930_1829'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instructor',
            options={},
        ),
        migrations.AlterModelOptions(
            name='learner',
            options={},
        ),
        migrations.AddField(
            model_name='institutionuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='Date when user was created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='institutionuser',
            name='locale',
            field=models.CharField(default=None, help_text='Default locale for this user', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='institutionuser',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text='Last user modification'),
        ),
    ]
