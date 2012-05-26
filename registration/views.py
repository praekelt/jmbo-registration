'''
Created on 25 May 2012

@author: euan
'''
import datetime

from django import http
from django.contrib import messages
from django.contrib.auth import login, get_backends
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, UpdateView, DetailView
from django.shortcuts import get_object_or_404

from preferences import preferences

from registration import models

#==============================================================================
class RegistrationView(FormView):
    
    @property
    def show_age_gateway(self):
        return preferences.GeneralPreferences.show_age_gateway and not self.request.COOKIES.get('age_gateway_passed')
    
    #--------------------------------------------------------------------------
    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        kwargs.update({ 'show_age_gateway' : self.show_age_gateway })
        return kwargs
    
    #--------------------------------------------------------------------------
    def form_valid(self, form):
        member = form.save()
        
        backend = get_backends()[0]
        member.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(self.request, member)            
        
        response = http.HttpResponseRedirect(reverse('join-finish'))

        # Set cookie if age gateway applicable. Can't delegate to form :(
        if self.show_age_gateway:
            now = datetime.datetime.now()
            expires = now.replace(year=now.year+10)
            response.set_cookie('age_gateway_passed', value=1, expires=expires)

        msg = _("You have successfully signed up to the site.")
        messages.success(self.request, msg, fail_silently=True)
        
        return response

#==============================================================================
class MemberUpdateView(UpdateView):
    
    #--------------------------------------------------------------------------
    def get_object(self):
        return self.request.user.member

#==============================================================================
class RedirectFromToken(DetailView):
    
    #--------------------------------------------------------------------------
    def dispatch(self, request, *args, **kwargs):
        token_obj = get_object_or_404(models.URLToken, token=kwargs['token'])
        return http.HttpResponseRedirect(token_obj.url)

#==============================================================================
class OffSiteInviteView(DetailView):
    
    #--------------------------------------------------------------------------
    def dispatch(self, request, *args, **kwargs):
        invites = models.OffSiteInvite.objects.filter(from_user=kwargs['user_id'], 
                                               to_mobile=kwargs['to_mobile']).order_by('-id')
        if invites:
            request.session['invitation'] = invites[0]
            return http.HttpResponseRedirect(reverse('join'))
        else:
            return http.Http404('huh?')
