from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models

from .models import Semester, EdClasses, Student, Rubric, Row, Enrollment, Assignment
#For user creation


#For admin page

class EnrollmentAdmin(admin.ModelAdmin):
	model = Enrollment
	fields = ('student', 'rubriccompleted','edclass')
	#list_display = ('student', 'rubriccompleted', 'semester', 'edclass')
	actions = None

	# The method below turns a readonly field if the user is editing the semester instance
	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ('student','edclass',)
		return self.readonly_fields
	
	def has_delete_permission(self, request, obj=None):
		return False


# The inline enrollment form for EdClass does not work because you can
# change the semester after creating the enrollment (do not want)
# You can edit out this functionality if the Enrollment is included in the Admin page
# but not as inline
#class EnrollmentAdmin1(admin.TabularInline):
#	model = Enrollment
#	readonly_fields = ('semester',)
#	fields = ('student', 'rubriccompleted', 'semester')
#	extra = 1

"""	
## Once again you cannot make an inline read only AND give the functionality
## to add more objects. Unfortunately
class EdClassSemesterInline(admin.TabularInline):
	model = EdClassSemester
	extra = 1
	actions = None
	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ('semester','keyrubric')
		return self.readonly_fields
	
	def has_delete_permission(self, request, obj=None):
		return False
		
	#def has_add_permission(self, request):
		#return False
		
"""

class EdClassAdmin(admin.ModelAdmin):
	#inlines = (EdClassSemesterInline,)
	
	#This only shows the template
	#def formfield_for_manytomany(self, db_field, request, **kwargs):
	#	if db_field.name == "keyrubric":
	#		kwargs["queryset"] = Rubric.objects.filter(template=True)
	#		return super(EdClassAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
	
	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ('crn','coursenumber','subject', 'sectionnumber')
		return self.readonly_fields
		
	def has_delete_permission(self, request, obj=None):
		return False



class EdClassSemesterAdmin(admin.ModelAdmin):
	actions = None
	
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == "keyrubric":
			kwargs["queryset"] = Rubric.objects.filter(template=True)
			return super(EdClassSemesterAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
	
	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ('edclass','semester','keyrubric')
		return self.readonly_fields
		
	def has_delete_permission(self, request, obj=None):
		return False
		
	
# The two classes below make the rows in the rubric app inline rows
# But the admin cannot edit a row after the fact they can only add a row			
class RowAdminInline(admin.TabularInline):
	model = Row
	extra = 0
	readonly_fields = ['name','row_choice', 'excellenttext', 'proficienttext', 'satisfactorytext','unsatisfactorytext',]
	can_delete = False
	
	def has_add_permission(self, request):
		return False
	
class AddRowAdminInline(admin.TabularInline):
	model = Row
	extra = 0
	fields =['name','row_choice', 'excellenttext', 'proficienttext', 'satisfactorytext','unsatisfactorytext',]
	
	def has_change_permission(self,request, obj=None):
		return False

class RubricAdmin(admin.ModelAdmin):
	inlines = (RowAdminInline, AddRowAdminInline,)
	actions = None
	
	def get_queryset(self, request):
		return Rubric.objects.filter(template=True)
		
	def has_delete_permission(self, request, obj=None):
		return False

class SemesterAdmin(admin.ModelAdmin):
	actions = None
	
	def has_delete_permission(self, request, obj=None):
		return False



# Register your models here.

admin.site.register(Assignment, EdClassSemesterAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(EdClasses, EdClassAdmin)
admin.site.register(Student)
admin.site.register(Rubric, RubricAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)

