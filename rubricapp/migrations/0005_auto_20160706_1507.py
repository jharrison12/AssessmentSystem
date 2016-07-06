# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rubricapp', '0004_edclasses_semester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='text',
            field=models.TextField(default='201530'),
        ),
    ]
