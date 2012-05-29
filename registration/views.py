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
from django.views.generic import FormView, CreateView, UpdateView, DetailView
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
        kwargs.update({ 'show_age_gateway' : self.show_age_gateway,
                        'offsite_invite' : self.request.session['invitation'] if self.request.session.has_key('invitation') else None 
                        })
        return kwargs
    
    #--------------------------------------------------------------------------
    def form_valid(self, form):
        member = form.save()
        
        offsite_invite_id = form.cleaned_data['offsite_invite']
        if offsite_invite_id:
            models.OffSiteInvite.objects.get(pk=offsite_invite_id).accept(member)
            
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
class CreateOffSiteInviteView(CreateView):
    
    #--------------------------------------------------------------------------
    def get_initial(self):
        return {'from_member' : self.request.user.member}
    
    #--------------------------------------------------------------------------
    def form_valid(self, form):
        msg = _("Your invitation has been sent.")
        messages.success(self.request, msg, fail_silently=True)
        return super(CreateOffSiteInviteView, self).form_valid(form)

#==============================================================================
class AcceptOffSiteInviteView(DetailView):
    
    #--------------------------------------------------------------------------
    def dispatch(self, request, *args, **kwargs):
        invites = models.OffSiteInvite.objects.filter(from_member=kwargs['member_id'], 
                                                      to_mobile_number=kwargs['to_mobile_number']).order_by('-id')
        if invites:
            request.session['invitation'] = invites[0]
            return http.HttpResponseRedirect(reverse('join'))
        else:
            return http.Http404('huh?')


