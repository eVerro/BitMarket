from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    url = models.URLField("Website", blank=True)
    company = models.CharField(max_length=50, blank=True)