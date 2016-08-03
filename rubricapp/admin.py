from django.contrib import admin

from .models import Semester, EdClasses, Student, Rubric, Row, EdClassAdmin, RubricAdmin

admin.site.register(Semester)
admin.site.register(EdClasses, EdClassAdmin)
admin.site.register(Student)
admin.site.register(Rubric, RubricAdmin)
admin.site.register(Row)

# Register your models here.
