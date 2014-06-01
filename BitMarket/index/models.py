# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import datetime

# Create your models here. TEST
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    url = models.URLField("Website", blank=True)
    company = models.CharField(max_length=50, blank=True)

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
    