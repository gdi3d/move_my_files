# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskPool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(choices=[(0, 'On queue'), (1, 'Runing'), (2, 'Finish :)'), (3, 'Fail :(')])),
                ('action', models.SmallIntegerField(choices=[(0, 'Upload'), (1, 'Download')])),
                ('source_pathname', models.CharField(help_text='Once downloaded this will be the pathname on local disk', max_length=255, verbose_name='Source Location', blank=True)),
                ('target_pathname', models.CharField(max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('log', models.TextField(null=True, blank=True)),
                ('task', models.ForeignKey(to='main.Task')),
            ],
        ),
    ]
