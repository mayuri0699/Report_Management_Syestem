# Generated by Django 4.2.16 on 2025-05-11 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportcard',
            name='pdf_url',
            field=models.FileField(blank=True, null=True, upload_to='reportcards/'),
        ),
    ]
