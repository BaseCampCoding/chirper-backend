from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class ChirperUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
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
        user = User(username=username, email=email)
        user.set_password(password)
        user.full_clean()
        user.save()
        chirper = ChirperUser(user=user, name=name)
        try:
            chirper.full_clean()
        except ValidationError as e:
            user.delete()
            raise e
        chirper.save()
        return chirper

    def chirp(self, message):
        '`ChirperUser.chirp` will create a new chirp with the provided message and `self` as the author'
        return Chirp.objects.create(author=self, message=message)

    def feed(self):
        '`ChirperUser.feed` returns a queryset representing all `Chirp`s that belong to `self`\'s feed.'
        return self.chirp_set.all().order_by('date')


class Chirp(models.Model):
    message = models.CharField(max_length=280)
    author = models.ForeignKey(ChirperUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} ({}): {}'.format(self.author.username, self.date,
                                    self.message)
