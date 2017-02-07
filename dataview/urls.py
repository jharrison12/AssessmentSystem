from django.conf.urls import include, url
from dataview import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

app_name='dataview'
urlpatterns = [ 
    # Examples:
	 url(r'^$', views.home_page, name='home'),
	 url(r'^student/$', views.student_view, name='student_view'),
	 url(r'^student/(?P<lnumber>[0-9]+)/$', views.student_data_view, name='student_data_view'),
	 url(r'^student/(?P<lnumber>[0-9]+)/(?P<rubricname>\w+)/$', views.student_rubric_data_view, name="student_rubric_data_view"),
	 url(r'^class/$', views.semester_ed_class_view, name='edclass_view'),
	 url(r'^class/(?P<semester>[0-9]{6})/$', views.ed_class_view, name="semesterclassview"),
	 url(r'^class/(?P<semester>[0-9]{6})/(?P<edclass>EG[0-9]+)/$', views.ed_class_assignment_view, name='ed_class_assignment_view'),
	 url(r'^class/(?P<semester>[0-9]{6})/(?P<edclass>EG[0-9]+)/(?P<assignmentname>\w+)/$', views.ed_class_data_view, name='ed_class_data_view'),
	 ]
