# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rubricapp', '0002_semester_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='EdClasses',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.TextField(default='')),
            ],
        ),
    ]
