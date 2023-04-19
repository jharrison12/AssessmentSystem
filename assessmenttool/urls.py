from django.conf.urls import include, url
from django.urls import path
from rubricapp import views
from django.contrib.auth import views as auth_views
from rubricapp.forms import PwordChangeForm
from dataview import urls
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

app_name = 'assessment'


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    # Examples:
	 url(r'^assessment/', include('rubricapp.urls',namespace="rubricapp")), 
	 url(r'^data/', include('dataview.urls',namespace="dataview")),
	 url(r'^user/', views.user_page, name='userpage'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
	#url(r'^password_change/$', auth_views.password_change, {'password_change_form': PwordChangeForm}), 
    url('^', include('django.contrib.auth.urls',)),
]
else:
    urlpatterns = [
        # Examples:
        url(r'^assessment/', include('rubricapp.urls', namespace="rubricapp")),
        url(r'^data/', include('dataview.urls', namespace="dataview")),
        url(r'^user/', views.user_page, name='userpage'),
        # Uncomment the admin/doc line below to enable admin documentation:
        # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        # Uncomment the next line to enable the admin:
        path('admin/', admin.site.urls),
        # url(r'^password_change/$', auth_views.password_change, {'password_change_form': PwordChangeForm}),
        url('^', include('django.contrib.auth.urls', )),
]
