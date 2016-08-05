from django.contrib import admin

from .models import Semester, EdClasses, Student, Rubric, Row, Enrollment

#For admin page
class EnrollmentAdmin(admin.TabularInline):
	model = Enrollment
	extra = 1

class EdClassAdmin(admin.ModelAdmin):
	inlines = (EnrollmentAdmin,)
	
	#This only shows the template
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == "keyrubric":
			kwargs["queryset"] = Rubric.objects.filter(template=True)
			return super(EdClassAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
	

	
class RowAdmin(admin.TabularInline):
	model = Row
	extra =1

class RubricAdmin(admin.ModelAdmin):
	inlines = (RowAdmin,)
	
	def get_queryset(self, request):
		return Rubric.objects.filter(template=True)




# Register your models here.


admin.site.register(Semester)
admin.site.register(EdClasses, EdClassAdmin)
admin.site.register(Student)
admin.site.register(Rubric, RubricAdmin)
admin.site.register(Row)

