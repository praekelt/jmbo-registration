'''
Created on 25 May 2012

@author: euan
'''
from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(
        r'^join/$',
        'foundry.views.join',
        {},
        name='join',
    ),
)