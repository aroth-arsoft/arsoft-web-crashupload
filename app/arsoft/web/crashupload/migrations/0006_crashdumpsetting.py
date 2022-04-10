# Generated by Django 4.0.3 on 2022-04-10 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crashupload', '0005_crashdumpproject_alter_crashdumpstate_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrashDumpSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name', max_length=64, unique=True, verbose_name='Name')),
                ('value', models.CharField(help_text='Value', max_length=1024, verbose_name='Value')),
            ],
            options={
                'verbose_name': 'Setting',
                'verbose_name_plural': 'Settings',
            },
        ),
    ]
