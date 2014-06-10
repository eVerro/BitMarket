# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dajaxice.core import dajaxice_autodiscover, dajaxice_config# tutaj ciagle wykrywa blad, nie wiem czemu, ale powinno dzialac
from django.contrib import admin

admin.autodiscover()
dajaxice_autodiscover()

import os
ROOT_PATH = os.path.dirname(__file__)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'BitMarket.views.home', name='home'),
    # url(r'^BitMarket/', include('BitMarket.foo.urls')),
    
    url(r'^$', 'BitMarket.index.views.index',name='home'),
    (r'^aboutus/', 'BitMarket.index.views.aboutus'),
    (r'^market/', 'BitMarket.index.views.market'),
    (r'^contact/', 'BitMarket.index.views.contact'),
    (r'^user/login/$','BitMarket.index.views.login'),
    (r'^user/logout/$', 'BitMarket.index.views.logout_view'),
    (r'^user/registerpage/$','BitMarket.index.views.register_view'),
    (r'^user/gldc/$','BitMarket.index.views.gldc_view'),
    (r'^user/ltc/$','BitMarket.index.views.ltc_view'),
    (r'^user/user/$','BitMarket.index.views.user'),
    (r'^user/register/$', 'BitMarket.index.register.register'),
    (r'^user/confirm/$', 'BitMarket.index.register.register'),
    (r'^user/confirm/(?P<code>\d+)/$','BitMarket.index.register.checkConfirmLink'),
    (r'^registrationconfirm/(?P<code>\d+)/$','BitMarket.index.register.checkConfirmLink'),
    (r'^ajax/ajaxTest/$','BitMarket.index.views.ajaxTest'),
    (dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    (r'^image/(?P<path>.*)$', 'django.views.static.serve',{'document_root': ROOT_PATH + '/media/image/'}),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # Testowanie modelu
    # def newCommission(self, source_amount, destination_amount, wallet_source, wallet_destination, dead_line):
    (r'^nc/', 'BitMarket.index.views.testNewCommission'),
    # def purchase(self, purchased_commission):
    (r'^pu/', 'BitMarket.index.views.testPurchase'),
    # def withdraw(self, wallet, wallet_address, amount):
    (r'^wir/', 'BitMarket.index.views.testWithdrawRequest'),
    # def confim(self, user, code):
    (r'^wi/(?P<code>\d+)/', 'BitMarket.index.views.testWithdraw'),
    # def deposit(self, wallet, wallet_address, amount):
    (r'^de/', 'BitMarket.index.views.testDeposit'),
    # def cancelCommission(self, commission):
    (r'^cc/', 'BitMarket.index.views.testCancelCommission'),
    # def cancelCommission(self, commission):
    (r'^cc/', 'BitMarket.index.views.testCancelCommission'),
    # def cancelCommission(self, commission):
    (r'^cc/', 'BitMarket.index.views.testCancelCommission'),
    # def getExchangeHistory(cryptocurrency_sold, cryptocurrency_bought):
    (r'^geh/', 'BitMarket.index.views.getExchangeHistory'),
    # def getBoughtHistory(cryptocurrency_sold, cryptocurrency_bought):
    (r'^gbh/', 'BitMarket.index.views.getBoughtHistory'),
    # getCommissions(cryptocurrency_first=None, cryptocurrency_second=None, sort=None):
    (r'^gco/', 'BitMarket.index.tests.getCommissions'),
)
urlpatterns += staticfiles_urlpatterns()