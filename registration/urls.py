'''
Created on 25 May 2012

@author: euan
'''
from django.conf.urls.defaults import patterns, url

from registration import forms, views

urlpatterns = patterns('',
    url(
        r'^join/$',
        views.RegistrationView.as_view(form_class=forms.JoinForm,
                                       template_name='registration/join.html'),
        name='join',
        ),
    
    url(
        r'^join-finish/$',
        views.MemberUpdateView.as_view(form_class=forms.JoinFinishForm,
                                       template_name='registration/join_finish.html',
                                       success_url='/'),
        name='join-finish',
        ),
    
    url(r'^offsite_invite/$',
        views.CreateOffSiteInviteView.as_view(form_class=forms.OffsiteInviteForm,
                                              template_name='registration/offsite_invite.html',
                                              success_url='/friends/my-friends/'),
        name='create_offsite_invite'
        ),
    
    url(r'^accept_invite/(?P<member_id>\d+)/(?P<to_mobile_number>[0-9]{10,13})/$',
        views.AcceptOffSiteInviteView.as_view(),
        name='accept_offsite_invite'
        ),

    url(r'^t/(?P<token>[a-z0-9]{8})/$', 
        views.RedirectFromToken.as_view(), 
        name='redirect_from_token'
        ),
                       
#    url(r'^token/(?P<token>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', 
#        views.RedirectFromToken.as_view(), 
#        name='redirect_from_token'
#        ),
)

#   url = 'http://%s/token/%s' % (Site.objects.get_current(), self.token)