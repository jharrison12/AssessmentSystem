from django.conf.urls import include, url
from rubricapp import views
from django.contrib.auth import views as auth_views
from rubricapp.forms import ValidatingPasswordChangeForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [ 
    # Examples:
	 url(r'^$', views.home_page, name='home'),
	 url(r'^(?P<semester>\d+)/$', views.semester_page, name='semester'),
	 url(r'^(?P<semester>\d+)/(?P<edclass>EG[0-9]{4})/$', views.student_page, name='student'),
	 url(r'^(?P<semester>\d+)/(?P<edclass>EG[0-9]{4})/(?P<studentname>[0-9]+)/$', views.rubric_page, name="rubricpage"),
    # url(r'^assessmenttool/', include('assessmenttool.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'^password_change/$', auth_views.password_change, {'password_change_form': ValidatingPasswordChangeForm}), 
    url('^', include('django.contrib.auth.urls',)),
]
