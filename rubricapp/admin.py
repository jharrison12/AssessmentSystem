from django.contrib import admin

from .models import Semester, EdClasses, Student, Rubric, Row

admin.site.register(Semester)
admin.site.register(EdClasses)
admin.site.register(Student)
admin.site.register(Rubric)
admin.site.register(Row)

# Register your models here.
