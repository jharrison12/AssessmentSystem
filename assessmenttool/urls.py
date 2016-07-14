from django.conf.urls import patterns, include, url
from rubricapp import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [ 
    # Examples:
     url(r'^$', views.home_page, name='home'),
     url(r'^(\d+)/$', 'rubricapp.views.semester_page', name='semester'),
     url(r'^(?P<edclass>EG[0-9]{4})/$', 'rubricapp.views.student_page', name='student'),
	 url(r'^(?P<edclass>EG[0-9]{4})/(?P<studentname>[A-Za-z]+)/$', views.rubric_page, name="rubricpage"),
    # url(r'^assessmenttool/', include('assessmenttool.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
