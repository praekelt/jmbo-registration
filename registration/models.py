'''
Created on 25 May 2012

@author: euan
'''
import random, urllib, urllib2

from django.db import models
from django.contrib.sites.models import Site

from foundry.models import Member
from friends.models import MemberFriend

POPULATION = ['0','1','2','3','4','5','6','7','8','9',
              'a','b','c','d','e','f','g','h','i','j','k','l','m',
              'n','o','p','q','r','s','t','u','v','w','x','y','z']
SIZE = 8

#==============================================================================
class URLToken(models.Model):

    token = models.CharField(max_length=8)
    url = models.CharField(max_length=256)

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return self.url
    
    def gen_token(self, population, size):
        token = ''.join(random.sample(population, size))
        try:
            URLToken.objects.get(token=token)
            return self.gen_token(population, size)
        except URLToken.DoesNotExist:
            return token
    
    #--------------------------------------------------------------------------
    def save(self, *args, **kwargs):
        """
        Generates a tiny_url on the fly.
        """
        if not self.token:
            self.token = self.gen_token(POPULATION, SIZE)
            
        super(URLToken, self).save(*args, **kwargs)
            
#==============================================================================
class OffSiteInvite(models.Model):
    
    INVITE_STATUS = (
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
    )
    
    from_member = models.ForeignKey(Member, related_name='invitations_sent') 
    to_friend_name = models.CharField(max_length=64)
    to_mobile_number = models.CharField(max_length=64)
    accepted_member = models.ForeignKey(Member, null=True, blank=True)
    member_friendship = models.ForeignKey(MemberFriend, null=True, blank=True)
    url_token = models.ForeignKey(URLToken)
    status = models.CharField(max_length=16, choices=INVITE_STATUS, default='invited')
    created = models.DateTimeField(auto_now_add=True)

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return 'Invitation from %s to %s' % (self.from_member,
                                             self.to_mobile_number)
    
    #--------------------------------------------------------------------------
    def save(self, *args, **kwargs):
        """
        Generates a URLToken as well.
        """
        if not self.id:
            url = 'http://%s/accept_invite/%d/%s/' % (Site.objects.get_current(), 
                                                      self.from_member.id, 
                                                      self.to_mobile_number)
            self.url_token = URLToken.objects.create(url=url)
            
        super(OffSiteInvite, self).save(*args, **kwargs)
        
    #--------------------------------------------------------------------------
    def accept(self, acceptee, *args, **kwargs):
        """
        Accept invitation and reward invitor.
        """
        self.accepted_member = acceptee
        self.status = 'accepted'
        self.member_friendship = MemberFriend.objects.create(member=self.from_member,
                                                             friend=self.accepted_member)
        self.save()
        self.member_friendship.accept()
    
    
    