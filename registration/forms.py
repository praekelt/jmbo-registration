'''
Created on 25 May 2012

@author: euan
'''
import re
import datetime

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.models import Site
from django.utils.translation import ugettext, ugettext_lazy as _

from foundry.ambientmobile import AmbientSMS, AmbientSMSError

from preferences import preferences
from jmbo.forms import as_div

from foundry.models import Member, DefaultAvatar, Country
from foundry.forms import TermsCheckboxInput, RememberMeCheckboxInput
from foundry.widgets import OldSchoolDateWidget

from registration import models

class ViaSMSCheckboxInput(forms.widgets.CheckboxInput):

    def render(self, *args, **kwargs):
        result = super(ViaSMSCheckboxInput, self).render(*args, **kwargs)
        return result + ugettext("by SMS")
    
class ViaEmailCheckboxInput(forms.widgets.CheckboxInput):

    def render(self, *args, **kwargs):
        result = super(ViaEmailCheckboxInput, self).render(*args, **kwargs)
        return result + ugettext("by Email")

class JoinForm(UserCreationForm):
    """Custom join form"""
    accept_terms = forms.BooleanField(required=True, label="", widget=TermsCheckboxInput)
    offsite_invite = forms.IntegerField(required=False, widget=forms.HiddenInput())
    remember_me = forms.BooleanField(required=False, initial=False, label="", widget=RememberMeCheckboxInput)
    
    class Meta:
        model = Member

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data["mobile_number"]
        if not re.match(r'[\+]?[0-9]*$', mobile_number):
            raise forms.ValidationError(_("Please enter a valid number"))
        if not mobile_number.startswith(settings.COUNTRY_CODE):
            raise forms.ValidationError(_("Sorry, we don't recognise that number. Make sure you add %(country_code)s in front of your number and don't leave any spaces." % {'country_code' : settings.COUNTRY_CODE}))
        return mobile_number

    def clean(self):
        cleaned_data = super(JoinForm, self).clean()

        # Validate required fields
        required_fields = preferences.RegistrationPreferences.required_fields
        if self.show_age_gateway:
            if 'country' not in required_fields:
                required_fields.append('country')
            if 'dob' not in required_fields:
                required_fields.append('dob')
        for name in required_fields:
            value = self.cleaned_data.get(name, None)
            if not value:
                message = _("This field is required.")

        # Validate unique fields
        unique_fields = preferences.RegistrationPreferences.unique_fields
        for name in unique_fields:
            value = self.cleaned_data.get(name, None)
            if value is not None:
                di = {'%s__iexact' % name:value}
                if Member.objects.filter(**di).count() > 0:
                    message =_("The %(pretty_name)s is already in use. \
Please supply a different %(pretty_name)s." % {'pretty_name': self.fields[name].label.lower()}
                    )
                    self._errors[name] = self.error_class([message])

        # Age gateway fields
        if self.show_age_gateway:
            country = cleaned_data.get('country')
            dob = cleaned_data.get('dob')
            if country and dob:
                today = datetime.date.today()
                if dob > today.replace(today.year - country.minimum_age):
                    msg = "You must be at least %s years of age to use this site." \
                        % country.minimum_age
                    raise forms.ValidationError(_(msg))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.show_age_gateway = kwargs.pop('show_age_gateway')
        
        # Set-up the offsite invitation defaults.
        offsite_invite = kwargs.pop('offsite_invite')
        if offsite_invite:
            self.base_fields['offsite_invite'].initial = offsite_invite.id 
            self.base_fields['first_name'].initial = offsite_invite.to_friend_name
            self.base_fields['mobile_number'].initial = offsite_invite.to_mobile_number
            
        super(JoinForm, self).__init__(*args, **kwargs)
       
        # Set date widget for date field
        for name, field in self.fields.items():            
            if isinstance(field, forms.fields.DateField):
                field.widget = OldSchoolDateWidget()

        display_fields = preferences.RegistrationPreferences.display_fields
        if self.show_age_gateway:
            if 'country' not in display_fields:
                display_fields.append('country')
            if 'dob' not in display_fields:
                display_fields.append('dob')
        for name, field in self.fields.items():
            # Skip over protected fields
            if name in ('id', 'username', 'password1', 'password2', 'accept_terms', 'offsite_invite', 'remember_me'):
                continue
            if name not in display_fields:
                del self.fields[name]
            
        # Set some fields required
        required_fields = preferences.RegistrationPreferences.required_fields
        if self.show_age_gateway:            
            if 'country' not in required_fields:
                required_fields.append('country')
            if 'dob' not in required_fields:
                required_fields.append('dob')
        for name in required_fields:
            field = self.fields.get(name, None)
            if field and not field.required:
                field.required = True

        # Remove accept_terms if terms and conditions not set
        if not preferences.GeneralPreferences.terms_and_conditions:
            del self.fields['accept_terms']

        # Make some messages and labels more reassuring
        self.fields['username'].help_text = _("This name is visible to other users on the site.")
        self.fields['password1'].help_text = None
        if self.fields.has_key('email'):
            self.fields['email'].help_text = _("Your email address is required in case you lose your password.")
        if self.fields.has_key('mobile_number'):
            # There is somebug in Django that does not allow translation to be
            # applied. Workaround.
            self.fields['mobile_number'].label = _("Mobile number")
            self.fields['mobile_number'].help_text = _("We need your number with the %(country_adjective)s dialing code. Example: %(sample_number)s.") % {'sample_number' : settings.REGISTRATION_SAMPLE_NUMBER,
                                                                                                                                                          'country_adjective' : settings.COUNTRY_ADJECTIVE}
        
        if self.fields.has_key('receive_sms'):
            self.fields['receive_sms'].widget =  ViaSMSCheckboxInput()
            self.fields['receive_sms'].label = _("Yes, I would like to hear more from Guinness")
        
        if self.fields.has_key('receive_email'):
            self.fields['receive_email'].widget =  ViaEmailCheckboxInput()
            self.fields['receive_email'].label = ""
            
        if self.fields.has_key('country'):
            self.fields['country'].label = _("Country of Residence")
            self.fields['country'].initial = Country.objects.all()[0] if Country.objects.all() else None
            
        if self.fields.has_key('gender'):
            self.fields['gender'].label = _("Gender")
            
        if self.fields.has_key('dob'):
            self.fields['dob'].label = _("Date of birth")
            
        if self.fields.has_key('city'):
            self.fields['city'].label = _("City")
        
    as_div = as_div
    
class JoinFinishForm(forms.ModelForm):
    """Show avatar selection form"""

    class Meta:
        model = Member
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super(JoinFinishForm, self).__init__(*args, **kwargs)

        self.fields['image'].label = _("Upload a picture")
        self.fields['image'].help_text = _("JPG, GIF or PNG accepted. Square is best. Keep it under 1MB.")
        self.fields['image'].widget = forms.FileInput()
        
        self.default_avatars = DefaultAvatar.objects.all()

    def clean(self):
        cleaned_data = super(JoinFinishForm, self).clean()
        if not cleaned_data.get('image'):
            if not self.data.has_key('default_avatar_id'):
                raise forms.ValidationError(_("Please upload or select a picture."))
        return cleaned_data

    def save(self, commit=True):
        instance = super(JoinFinishForm, self).save(commit=commit)

        # Set image from default avatar if required
        if not instance.image and self.data.has_key('default_avatar_id'):
            obj = DefaultAvatar.objects.get(id=self.data['default_avatar_id'])
            instance.image = obj.image
            if commit:
                instance.save()

        return instance

    as_div = as_div
    

    
#==============================================================================
class OffsiteInviteForm(forms.ModelForm):
    """Allows a user to invite another user, who does not have an account yet."""    

    #--------------------------------------------------------------------------
    class Meta:
        model = models.OffSiteInvite
        fields = ('from_member','to_friend_name','to_mobile_number',)
    
    
    def __init__(self, *args, **kwargs):
        
        self.base_fields['from_member'].widget = forms.HiddenInput()
        self.base_fields['to_friend_name'].label = _(u'Friend\'s name')
        self.base_fields['to_mobile_number'] = forms.IntegerField(label=_(u'Friend\'s mobile number'))
        self.base_fields['to_mobile_number'].default_error_messages['invalid'] = 'You should enter only numbers in this field.'
        
        super(OffsiteInviteForm, self).__init__(*args, **kwargs)
    
    #--------------------------------------------------------------------------    
    def clean(self):
        """Check if the mobile number is already registered."""
        if self.cleaned_data.has_key('to_mobile_number'):
            try:
                Member.objects.get(mobile_number=self.cleaned_data['to_mobile_number'])
                raise forms.ValidationError(
                    _(u'Sorry, but someone with that mobile number already has an ' \
                      'account. Why not invite another friend?'))
            except Member.DoesNotExist:
                return self.cleaned_data
        
        return self.cleaned_data
        
    #--------------------------------------------------------------------------    
    def save(self, *args, **kwargs):
        
        invite = super(OffsiteInviteForm, self).save(*args, **kwargs)
        
        sms = AmbientSMS(
            settings.FOUNDRY['sms_gateway_api_key'], 
            settings.FOUNDRY['sms_gateway_password']
        )
        
        url = 'http://%s/token/%s/' % (Site.objects.get_current(), invite.url_token.token)
        
        content = u'%s, %s invites you to join %s.  ' \
                   'Click here to become a member: %s' % (invite.to_friend_name,
                                                          invite.from_member,
                                                          Site.objects.get_current(),
                                                          url)
        try:
            sms.sendmsg(content, [self.cleaned_data['to_mobile_number']])
        except AmbientSMSError:
            pass
        
        return invite
            
    as_div = as_div
    
    