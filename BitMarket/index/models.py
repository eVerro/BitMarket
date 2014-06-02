# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import datetime

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
    
    def confirm(self):
        user = UserProfile(self)
        user.url = self.url
        user.company = self.company
        user.phone_number = self.phone_number
        user.save()
        self.delete()
        
        
class Newss(models.Model):
    tytul = models.CharField(max_length=200)
    kategoria = models.CharField(max_length=20)
    pub_date = models.DateTimeField('data publikacji')
    text = models.CharField(max_length=2000)
    autor = models.CharField(max_length=20)
    obrazek = models.ImageField(upload_to='newsImage')
    def __unicode__(self):
        return self.tytul
    def was_published_today(self):
        return self.pub_date.date() == datetime.date.today()
    
admin.site.register(Newss)
