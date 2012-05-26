'''
Created on 25 May 2012

@author: euan
'''
from django.conf.urls.defaults import patterns, url, include

from registration import forms, views

urlpatterns = patterns('',
    url(
        r'^join/$',
        views.RegistrationView.as_view(form_class=forms.JoinForm,
                                       template_name='foundry/join.html'),
        name='join',
    ),
    
    url(
        r'^join-finish/$',
        views.MemberUpdateView.as_view(form_class=forms.JoinFinishForm,
                                       template_name='foundry/join_finish.html',
                                       success_url='/'),
        name='join-finish',
    ),
)

'foundry/join_finish.html'