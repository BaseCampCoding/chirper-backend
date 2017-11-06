from django.db import models
from django.contrib.auth.models import User


class ChirperUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True)
    location = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    joined = models.DateField(auto_now_add=True)


class Chirp(models.Model):
    message = models.CharField(max_length=280)
    author = models.ForeignKey(ChirperUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
