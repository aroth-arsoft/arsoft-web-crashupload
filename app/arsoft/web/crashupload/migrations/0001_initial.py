# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-24 18:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrashDumpAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the attachment', max_length=256, verbose_name='Name')),
                ('description', models.TextField(help_text='description of the attachment', max_length=8192, verbose_name='Description')),
                ('storageFile', models.CharField(help_text='path to the stored attachment file', max_length=256, verbose_name='Storage file')),
            ],
            options={
                'verbose_name': 'Crash attachment',
                'verbose_name_plural': 'Crash attachments',
            },
        ),
        migrations.CreateModel(
            name='CrashDumpLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the link', max_length=256, null=True, verbose_name='Name')),
                ('url', models.TextField(help_text='URL', max_length=2048, verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Crash link',
                'verbose_name_plural': 'Crash links',
            },
        ),
        migrations.CreateModel(
            name='CrashDumpModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crashid', models.CharField(help_text='unique identifier of the crash', max_length=36, unique=True, verbose_name='Crash id')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('applicationName', models.CharField(help_text='name of the application which caused the crash', max_length=256, verbose_name='Application name')),
                ('applicationFile', models.CharField(help_text='file of the application which caused the crash', max_length=512, verbose_name='Application file')),
                ('clientHostName', models.CharField(help_text='full qualified host name of the client', max_length=256, null=True, verbose_name='Client FQDN')),
                ('clientUserName', models.CharField(help_text='username of the client', max_length=256, null=True, verbose_name='Client user')),
                ('productName', models.CharField(help_text='name of the product', max_length=256, verbose_name='Product name')),
                ('productVersion', models.CharField(help_text='version of the product', max_length=24, verbose_name='Product version')),
                ('productTargetVersion', models.CharField(help_text='target version of the product', max_length=24, verbose_name='Product target version')),
                ('buildType', models.CharField(choices=[('DEBUG', 'Debug'), ('RELWITHDEBINFO', 'Release with debug info'), ('RELEASE', 'Release'), ('MINSIZEREL', 'Minimum size release')], default='RELEASE', help_text='build type', max_length=16, verbose_name='Build type')),
                ('buildPostfix', models.CharField(choices=[('', 'None (release)'), ('d', 'Debug'), ('rd', 'Release with debug info'), ('r', 'Release'), ('rs', 'Minimum size release')], default='', help_text='build postfix', max_length=4, verbose_name='Build postfix')),
                ('machineType', models.CharField(choices=[('unknown', 'Unknown'), ('PC', 'PC'), ('Mac', 'Mac'), ('VirtualBox', 'VirtualBox'), ('VMWare', 'VMWare'), ('VPC', 'Virtual PC')], default='unknown', help_text='machine type', max_length=16, verbose_name='Machine type')),
                ('systemName', models.CharField(help_text='name of operating system', max_length=24, verbose_name='System name')),
                ('osVersion', models.CharField(help_text='version of operating system', max_length=24, verbose_name='OS version')),
                ('osRelease', models.CharField(help_text='release of operating system', max_length=24, verbose_name='OS release')),
                ('osMachine', models.CharField(help_text='machine of operating system', max_length=24, verbose_name='OS machine')),
                ('systemInfoData', models.TextField(help_text='system information', max_length=65536, null=True, verbose_name='System info')),
                ('gfxCapsFile', models.CharField(help_text='relative path to the gfxcaps file', max_length=256, null=True, verbose_name='GfxCaps file')),
                ('minidumpFile', models.CharField(help_text='relative path to the Minidump file', max_length=256, null=True, verbose_name='Minidump file')),
                ('minidumpReportTextFile', models.CharField(help_text='relative path to the Minidump text report file', max_length=256, null=True, verbose_name='Minidump text report file')),
                ('minidumpReportXMLFile', models.CharField(help_text='relative path to the Minidump XML report file', max_length=256, null=True, verbose_name='Minidump XML report file')),
                ('minidumpReportHTMLFile', models.CharField(help_text='relative path to the Minidump HTML report file', max_length=256, null=True, verbose_name='Minidump HTML report file')),
                ('coredumpFile', models.CharField(help_text='relative path to the Coredump file', max_length=256, null=True, verbose_name='Coredump file')),
                ('coredumpReportTextFile', models.CharField(help_text='relative path to the Coredump text report file', max_length=256, null=True, verbose_name='Coredump text report file')),
                ('coredumpReportXMLFile', models.CharField(help_text='relative path to the Coredump XML report file', max_length=256, null=True, verbose_name='Coredump XML report file')),
                ('coredumpReportHTMLFile', models.CharField(help_text='relative path to the Coredump HTML report file', max_length=256, null=True, verbose_name='Coredump HTML report file')),
            ],
            options={
                'verbose_name': 'Crash',
                'verbose_name_plural': 'Crashes',
            },
        ),
        migrations.CreateModel(
            name='CrashDumpState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='short name of the state', max_length=32, verbose_name='Name')),
                ('description', models.CharField(help_text='description of the attachment', max_length=256, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Crash state',
                'verbose_name_plural': 'Crash states',
            },
        ),
        migrations.AddField(
            model_name='crashdumpmodel',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crashupload.CrashDumpState'),
        ),
        migrations.AddField(
            model_name='crashdumplink',
            name='crash',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crashupload.CrashDumpModel'),
        ),
        migrations.AddField(
            model_name='crashdumpattachment',
            name='crash',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crashupload.CrashDumpModel'),
        ),
    ]
