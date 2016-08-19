from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Semester, EdClasses, Student, Rubric, Row, Enrollment
#For user creation


#For admin page

class EnrollmentAdmin(admin.ModelAdmin):
	model = Enrollment
	fields = ('student', 'rubriccompleted', 'semester', 'edclass')
	# The method below turns a readonly field if the user is editing the semester instance
	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ('semester',)
		return self.readonly_fields

# The inline enrollment form for EdClass does not work because you can
# change the semester after creating the enrollment (do not want)
# You can edit out this functionality if the Enrollment is included in the Admin page
# but not as inline
#class EnrollmentAdmin1(admin.TabularInline):
#	model = Enrollment
#	readonly_fields = ('semester',)
#	fields = ('student', 'rubriccompleted', 'semester')
#	extra = 1
	


class EdClassAdmin(admin.ModelAdmin):
	#inlines = (EnrollmentAdmin1,)
	
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
admin.site.register(Enrollment, EnrollmentAdmin)

