from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dajaxice.core import dajaxice_autodiscover, dajaxice_config# tutaj ciagle wykrywa blad, nie wiem czemu, ale powinno dzialac
from django.contrib import admin
admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'BitMarket.views.home', name='home'),
    # url(r'^BitMarket/', include('BitMarket.foo.urls')),
    
    url(r'^$', 'BitMarket.index.views.index',name='home'),
    (r'^aboutus/', 'BitMarket.index.views.aboutus'),
    (r'^user/login/$','BitMarket.index.views.login'),
    (r'^user/logout/$', 'BitMarket.index.views.logout_view'),
    (r'^user/registerpage/$','BitMarket.index.views.register_view'),
    (r'^user/register/$', 'BitMarket.index.views.register'),
    (r'^ajax/ajaxTest/$','BitMarket.index.views.ajaxTest'),
    (dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += staticfiles_urlpatterns()#bylo w tutorialu do ajaxa