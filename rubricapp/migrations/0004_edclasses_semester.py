# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rubricapp', '0003_edclasses'),
    ]

    operations = [
        migrations.AddField(
            model_name='edclasses',
            name='semester',
            field=models.ForeignKey(default=None, to='rubricapp.Semester'),
        ),
    ]
