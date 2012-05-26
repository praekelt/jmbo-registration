'''
Created on 25 May 2012

@author: euan
'''
import uuid, urllib, urllib2

from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from panomena_mobile.models import MsisdnField

#==============================================================================
class URLToken(models.Model):

    token = models.CharField(max_length=40)
    url = models.CharField(max_length=256)
    tiny_url = models.URLField()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return self.url
    
    #--------------------------------------------------------------------------
    def save(self, *args, **kwargs):
        """
        Generates a tiny_url on the fly.
        """
        if not self.token:
            self.token = uuid.uuid4()
        
        if not self.tiny_url:
            url = 'http://%s/token/%s' % (Site.objects.get_current(), self.token)
            self.tiny_url = urllib2.urlopen('http://tinyurl.com/api-create.php?url=%s' % urllib.quote(url)).read()
            
        super(URLToken, self).save(*args, **kwargs)
        
    
#==============================================================================
class OffSiteInvite(models.Model):
    
    INVITE_STATUS = (
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
    )
    
    from_user = models.ForeignKey(User, related_name='invitation_send') 
    to_mobile = MsisdnField()
    accepted_user = models.ForeignKey(User, null=True, blank=True)
    url_token = models.ForeignKey(URLToken)
    status = models.CharField(max_length=16, choices=INVITE_STATUS, default='invited')
    created = models.DateTimeField(auto_now_add=True)

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return 'Invitation from %s to %s' % (self.from_user.get_display_name(),
                                             self.to_mobile)
    
    #--------------------------------------------------------------------------
    def save(self, *args, **kwargs):
        """
        Generates a URLToken as well.
        """
        if not self.id:
            self.url_token = URLToken.objects.create(url='http://%s/accept_invite/%d/%s/' % (Site.objects.get_current(), 
                                                                                             self.from_user.id, 
                                                                                             self.to_mobile))
        super(OffSiteInvite, self).save(*args, **kwargs)
        
    #--------------------------------------------------------------------------
    def accept(self, acceptee, *args, **kwargs):
        """
        Accept invitation and reward invitor.
        """
        self.status = 'accepted'
        self.save()
