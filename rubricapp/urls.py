from django.urls import re_path
from rubricapp import views
from django.contrib.auth import views as auth_views
#from rubricapp.forms import ValidatingPasswordForm
from dataview import urls
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

app_name = 'rubricapp'
urlpatterns = [ 
    # Examples:
	 re_path(r'^$', views.home_page, name='home'),
	 re_path(r'^(?P<semester>\d+)/$', views.semester_page, name='semester'),
	 re_path(r'^(?P<semester>\d+)/(?P<edclass>(ED|EG)[0-9]{6})/$', views.assignment_page, name='student'),
	 re_path(r'^(?P<semester>\d+)/(?P<edclass>(ED|EG)[0-9]{6})/(?P<assignmentname>\w+)/$', views.student_page, name='assignment'),
	 re_path(r'^(?P<semester>\d+)/(?P<edclass>(ED|EG)[0-9]{6})/(?P<assignmentname>\w+)/(?P<studentname>[0-9]+)/$', views.rubric_page, name="rubricpage"),

]
