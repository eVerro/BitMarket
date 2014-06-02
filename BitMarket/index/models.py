# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User


# Create your models here. TEST
class UserProfile(User):
    url = models.URLField("Website", blank=True, unique=False)
    company = models.CharField(max_length=50, blank=True, unique=False)
    phone_number = models.CharField(max_length=13, blank=False, unique=False)
    
    def __unicode__(self):
        return '%s' % (self.username)

class UserNotConfirmed(User):
    url = models.URLField("Website", blank=True, unique=False)
    company = models.CharField(max_length=50, blank=True, unique=False)
    phone_number = models.CharField(max_length=13, blank=False, unique=False)
    code = models.CharField(max_length=30, blank=False, unique=True)
    
    class Meta():
        db_table = 'NotRegistredUser'
    
    def __unicode__(self):
        return 'Nie potwierdzony %s' % (self.username)
    
    def confim(self):
        user = UserProfile(self)
        user.url = self.url
        user.company = self.company
        user.phone_number = self.phone_number
        user.save()
        self.delete()