'''
Created on 25 May 2012

@author: euan
'''
import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import *

from preferences import preferences

#==============================================================================
class RegisterView(FormView):
    
    #--------------------------------------------------------------------------
    @property
    def show_age_gateway(self):
        return preferences.GeneralPreferences.show_age_gateway and not self.request.COOKIES.get('age_gateway_passed')
    
    #--------------------------------------------------------------------------
    def get_form_kwargs(self):
        kwargs = super(RegisterView, self).get_form_kwargs()
        kwargs.update({ 'show_age_gateway' : self.show_age_gateway })
        return kwargs
    
    #--------------------------------------------------------------------------
    def form_valid(self, form):
        member = form.save()
        login(self.request, member.user)
        
        response = HttpResponseRedirect(reverse('join-finish'))

        # Set cookie if age gateway applicable. Can't delegate to form :(
        if self.show_age_gateway:
            now = datetime.datetime.now()
            expires = now.replace(year=now.year+10)
            response.set_cookie('age_gateway_passed', value=1, expires=expires)

        msg = _("You have successfully signed up to the site.")
        messages.success(self.request, msg, fail_silently=True)
        
        return response
    