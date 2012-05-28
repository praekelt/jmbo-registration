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
from django.utils.translation import ugettext_lazy as _

from foundry.ambientmobile import AmbientSMS, AmbientSMSError

from preferences import preferences
from jmbo.forms import as_div

from foundry.models import Member, DefaultAvatar
from foundry.forms import TermsCheckboxInput
from foundry.widgets import OldSchoolDateWidget

from registration import models

class JoinForm(UserCreationForm):
    """Custom join form"""
    accept_terms = forms.BooleanField(required=True, label="", widget=TermsCheckboxInput)
    offsite_invite = forms.IntegerField(required=True, widget=forms.HiddenInput())
    
    class Meta:
        model = Member

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data["mobile_number"]
        if not re.match(r'[\+]?[0-9]*$', mobile_number):
            raise forms.ValidationError(_("Please enter a valid number"))
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
                    pretty_name = self.fields[name].label.lower()
                    message =_("The %(pretty_name)s is already in use. \
Please supply a different %(pretty_name)s." % {'pretty_name': pretty_name}
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
            if name in ('id', 'username', 'password1', 'password2', 'accept_terms', 'offsite_invite'):
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
        self.fields['password1'].help_text = _("We never store your password in its original form.")
        if self.fields.has_key('email'):
            self.fields['email'].help_text = _("Your email address is required in case you lose your password.")
        if self.fields.has_key('mobile_number'):
            # There is somebug in Django that does not allow translation to be
            # applied. Workaround.
            self.fields['mobile_number'].label = _("Mobile number")
            self.fields['mobile_number'].help_text = _("The number must be in \
international format and may start with a + sign. All other characters must \
be numbers. No spaces allowed. An example is +27821234567.")
        
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
        self.base_fields['to_mobile_number'].label = _(u'Friend\'s mobile number')
        
        super(OffsiteInviteForm, self).__init__(*args, **kwargs)
    
    #--------------------------------------------------------------------------    
    def clean(self):
        """Check if the mobile number is already registered."""
        try:
            Member.objects.get(mobile_number=self.cleaned_data['to_mobile_number'])
            raise forms.ValidationError(
                _(u'Sorry, but someone with that mobile number already has an ' \
                  'account. Why not invite another friend?'))
        except Member.DoesNotExist:
            return self.cleaned_data
        
    #--------------------------------------------------------------------------    
    def save(self, *args, **kwargs):
        
        invite = super(OffsiteInviteForm, self).save(*args, **kwargs)
        
        sms = AmbientSMS(
            settings.FOUNDRY['sms_gateway_api_key'], 
            settings.FOUNDRY['sms_gateway_password']
        )
        content = u'%s, %s invites you to join %s.  ' \
                   'Click here to become a member: %s' % (invite.to_friend_name,
                                                          invite.from_member,
                                                          Site.objects.get_current(),
                                                          invite.url_token.tiny_url)
        try:
            sms.sendmsg(content, [self.cleaned_data['to_mobile_number']])
        except AmbientSMSError:
            pass
        
        return invite
            
    as_div = as_div
    
#==============================================================================
class PerfectTeamChooseForm(forms.Form):
    """
    Pick a team.
    """    
    team = forms.ModelChoiceField(queryset=models.PerfectTeam.objects.all(),
                                  widget=forms.RadioSelect(),
                                  empty_label=None)
    
    as_div = as_div
    
#==============================================================================
class PerfectTeamInviteForm(forms.ModelForm):
    """
    Allows a user to invite 4 more users via the perfect team promotion. 
        No-one should have an account yet.
    """    
    
    #--------------------------------------------------------------------------
    class Meta:
        model = models.PerfectTeamEntry
        fields = ('team', 
                  'from_member',
                  'friend_1_name',
                  'friend_1_mobile_number',
                  'friend_2_name',
                  'friend_2_mobile_number',
                  'friend_3_name',
                  'friend_3_mobile_number',
                  'friend_4_name',
                  'friend_4_mobile_number',
                  )
    
    
    def __init__(self, *args, **kwargs):
        
        self.base_fields['team'].widget = forms.HiddenInput()
        self.base_fields['from_member'].widget = forms.HiddenInput()
        
        self.base_fields['friend_1_name'].label = _(u'Friend 1: %s' % kwargs['initial']['team'].player_1)
        if kwargs['initial']['team'].player_1_description:
            self.base_fields['friend_1_name'].label += ' (%s)' % kwargs['initial']['team'].player_1_description
        self.base_fields['friend_1_mobile_number'].label = _(u'Friend 1\'s mobile number')
        
        self.base_fields['friend_2_name'].label = _(u'Friend 2: %s' % kwargs['initial']['team'].player_2)
        if kwargs['initial']['team'].player_2_description:
            self.base_fields['friend_2_name'].label += ' (%s)' % kwargs['initial']['team'].player_2_description
        self.base_fields['friend_2_mobile_number'].label = _(u'Friend 2\'s mobile number')
        
        self.base_fields['friend_3_name'].label = _(u'Friend 3: %s' % kwargs['initial']['team'].player_3)
        if kwargs['initial']['team'].player_3_description:
            self.base_fields['friend_3_name'].label += ' (%s)' % kwargs['initial']['team'].player_3_description
        self.base_fields['friend_3_mobile_number'].label = _(u'Friend 3\'s mobile number')
        
        self.base_fields['friend_4_name'].label = _(u'Friend 4: %s' % kwargs['initial']['team'].player_4)
        if kwargs['initial']['team'].player_4_description:
            self.base_fields['friend_4_name'].label += ' (%s)' % kwargs['initial']['team'].player_4_description
        self.base_fields['friend_4_mobile_number'].label = _(u'Friend 4\'s mobile number')
        
        super(PerfectTeamInviteForm, self).__init__(*args, **kwargs)
    
    #--------------------------------------------------------------------------    
    def clean_friend_1_mobile_number(self):
        """Check if the mobile number is already registered."""
        if self.cleaned_data['friend_1_name'] and not self.cleaned_data['friend_1_mobile_number']:
            raise forms.ValidationError(
                _(u'You need to specify a mobile number.'))
        try:
            Member.objects.get(mobile_number=self.cleaned_data['friend_1_mobile_number'])
            raise forms.ValidationError(
                _(u'Sorry, but someone with that mobile number already has an ' \
                  'account. Why not invite another friend?'))
        except Member.DoesNotExist:
            return self.cleaned_data['friend_1_mobile_number']
    
    #--------------------------------------------------------------------------    
    def clean_friend_2_mobile_number(self):
        """Check if the mobile number is already registered."""
        if self.cleaned_data['friend_2_name'] and not self.cleaned_data['friend_2_mobile_number']:
            raise forms.ValidationError(
                _(u'You need to specify a mobile number.'))
        try:
            Member.objects.get(mobile_number=self.cleaned_data['friend_2_mobile_number'])
            raise forms.ValidationError(
                _(u'Sorry, but someone with that mobile number already has an ' \
                  'account. Why not invite another friend?'))
        except Member.DoesNotExist:
            return self.cleaned_data['friend_2_mobile_number']
    
    #--------------------------------------------------------------------------    
    def clean_friend_3_mobile_number(self):
        """Check if the mobile number is already registered."""
        if self.cleaned_data['friend_3_name'] and not self.cleaned_data['friend_3_mobile_number']:
            raise forms.ValidationError(
                _(u'You need to specify a mobile number.'))
        try:
            Member.objects.get(mobile_number=self.cleaned_data['friend_3_mobile_number'])
            raise forms.ValidationError(
                _(u'Sorry, but someone with that mobile number already has an ' \
                  'account. Why not invite another friend?'))
        except Member.DoesNotExist:
            return self.cleaned_data['friend_3_mobile_number']
    
    #--------------------------------------------------------------------------    
    def clean_friend_4_mobile_number(self):
        """Check if the mobile number is already registered."""
        if self.cleaned_data['friend_4_name'] and not self.cleaned_data['friend_4_mobile_number']:
            raise forms.ValidationError(
                _(u'You need to specify a mobile number.'))
        try:
            Member.objects.get(mobile_number=self.cleaned_data['friend_4_mobile_number'])
            raise forms.ValidationError(
                _(u'Sorry, but someone with that mobile number already has an ' \
                  'account. Why not invite another friend?'))
        except Member.DoesNotExist:
            return self.cleaned_data['friend_4_mobile_number']
        
    #--------------------------------------------------------------------------    
    def create_invite(self, from_member, friend_name, friend_mobile_number, team_player, team_player_description):
        
        invite = models.OffSiteInvite.objects.create(from_member=from_member, to_friend_name=friend_name, to_mobile_number=friend_mobile_number)
            
        content = u'%s, %s thinks you are the %s of your group of friends' % (friend_name, from_member, team_player)
        
        if team_player_description:
            content += u', %s' % team_player_description
            
        content += u'. Join m.gvip.com and let us know: %s' % invite.url_token.tiny_url
        try:
            AmbientSMS(settings.FOUNDRY['sms_gateway_api_key'], settings.FOUNDRY['sms_gateway_password']).sendmsg(content, [friend_mobile_number])
        except AmbientSMSError:
            pass
        
        return invite
        
    #--------------------------------------------------------------------------    
    def save(self, *args, **kwargs):
        
        entry = super(PerfectTeamInviteForm, self).save(*args, **kwargs)
        
        if self.cleaned_data['friend_1_mobile_number']:
            entry.friend_1_invite = self.create_invite(self.cleaned_data['from_member'], 
                                                       self.cleaned_data['friend_1_name'], 
                                                       self.cleaned_data['friend_1_mobile_number'], 
                                                       entry.team.player_1, 
                                                       entry.team.player_1_description)
        if self.cleaned_data['friend_2_mobile_number']:
            entry.friend_2_invite = self.create_invite(self.cleaned_data['from_member'], 
                                                       self.cleaned_data['friend_2_name'], 
                                                       self.cleaned_data['friend_2_mobile_number'], 
                                                       entry.team.player_2, 
                                                       entry.team.player_2_description)
        if self.cleaned_data['friend_3_mobile_number']:
            entry.friend_3_invite = self.create_invite(self.cleaned_data['from_member'], 
                                                       self.cleaned_data['friend_3_name'], 
                                                       self.cleaned_data['friend_3_mobile_number'], 
                                                       entry.team.player_3, 
                                                       entry.team.player_3_description)
        if self.cleaned_data['friend_4_mobile_number']:
            entry.friend_4_invite = self.create_invite(self.cleaned_data['from_member'], 
                                                       self.cleaned_data['friend_4_name'], 
                                                       self.cleaned_data['friend_4_mobile_number'], 
                                                       entry.team.player_4, 
                                                       entry.team.player_4_description)
            
        entry.save()
        
        return entry
            
    as_div = as_div
    
    