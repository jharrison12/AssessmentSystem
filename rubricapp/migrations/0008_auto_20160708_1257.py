# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rubricapp', '0007_student_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edclasses',
            name='semester',
        ),
        migrations.AddField(
            model_name='semester',
            name='classes',
            field=models.ManyToManyField(to='rubricapp.EdClasses'),
        ),
    ]
