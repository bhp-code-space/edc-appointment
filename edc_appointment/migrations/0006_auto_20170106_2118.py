# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-06 19:18
from __future__ import unicode_literals

from django.db import migrations, models
import edc_base.model_fields.hostname_modification_field
import edc_base.model_fields.userfield
import edc_base.utils


class Migration(migrations.Migration):

    dependencies = [
        ('edc_appointment', '0005_auto_20161221_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='created',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='hostname_created',
            field=models.CharField(blank=True, default='mac2-2.local', help_text='System field. (modified on create only)', max_length=50),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='hostname_modified',
            field=edc_base.model_fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='modified',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='user_created',
            field=edc_base.model_fields.userfield.UserField(blank=True, max_length=50, verbose_name='user created'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='user_modified',
            field=edc_base.model_fields.userfield.UserField(blank=True, max_length=50, verbose_name='user modified'),
        ),
        migrations.AlterField(
            model_name='historicalappointment',
            name='created',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='historicalappointment',
            name='hostname_created',
            field=models.CharField(blank=True, default='mac2-2.local', help_text='System field. (modified on create only)', max_length=50),
        ),
        migrations.AlterField(
            model_name='historicalappointment',
            name='hostname_modified',
            field=edc_base.model_fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50),
        ),
        migrations.AlterField(
            model_name='historicalappointment',
            name='modified',
            field=models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow),
        ),
        migrations.AlterField(
            model_name='historicalappointment',
            name='user_created',
            field=edc_base.model_fields.userfield.UserField(blank=True, max_length=50, verbose_name='user created'),
        ),
        migrations.AlterField(
            model_name='historicalappointment',
            name='user_modified',
            field=edc_base.model_fields.userfield.UserField(blank=True, max_length=50, verbose_name='user modified'),
        ),
    ]
