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
]
