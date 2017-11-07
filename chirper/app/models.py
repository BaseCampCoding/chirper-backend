from django.db import models
from django.contrib.auth.models import User


class ChirperUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True)
    location = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    joined = models.DateField(auto_now_add=True)

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @staticmethod
    def signup(name, username, email, password):
        '''`ChirperUser.signup` creates and returns a new `ChirperUser` with the provided data.
        
        To create the `ChirperUser`, it creates the underlying `django.contrib.auth.models.User`,
        and then creates the `ChirperUser`.
        
        Any errors during `User` creation or `ChirperUser` creation are unhandled by this method
        and will bubble up. This may change in the future.
        '''
        user = User.objects.create_user(username, email, password)
        return ChirperUser.objects.create(user=user, name=name)


class Chirp(models.Model):
    message = models.CharField(max_length=280)
    author = models.ForeignKey(ChirperUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
