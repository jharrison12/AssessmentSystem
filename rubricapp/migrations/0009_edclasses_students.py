# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rubricapp', '0008_auto_20160708_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='edclasses',
            name='students',
            field=models.ManyToManyField(to='rubricapp.Student'),
        ),
    ]
