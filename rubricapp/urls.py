from django.conf.urls import include, url
from rubricapp import views
from django.contrib.auth import views as auth_views
from rubricapp.forms import ValidatingPasswordForm
from dataview import urls
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

app_name = 'rubricapp'
urlpatterns = [ 
    # Examples:
	 url(r'^$', views.home_page, name='home'),
	 url(r'^(?P<semester>\d+)/$', views.semester_page, name='semester'),
	 url(r'^(?P<semester>\d+)/(?P<edclass>EG[0-9]{4})/$', views.student_page, name='student'),
	 url(r'^(?P<semester>\d+)/(?P<edclass>EG[0-9]{4})/(?P<studentname>[0-9]+)/$', views.rubric_page, name="rubricpage"),

]
