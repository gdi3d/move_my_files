from django.conf.urls import patterns, include, url
from django.contrib import admin

from main import views


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 's3backups.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^index/$', 'main.views.index', name='index'),
    #url(r'^login$', 'main.views.login', name='login'),
    #url(r'^login/validate$', 'main.views.user_login', name='user_login'),    
    #url(r'^accounts/', include('allauth.urls')),    
)