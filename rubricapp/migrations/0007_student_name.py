# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rubricapp', '0006_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='name',
            field=models.TextField(default=''),
        ),
    ]
