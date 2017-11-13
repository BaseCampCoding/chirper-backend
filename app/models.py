import secrets

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save


class ChirperUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    description = models.CharField(max_length=300, blank=True)
    location = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    joined = models.DateField(auto_now_add=True)

    def clean(self):
        if '@' in self.user.username:
            raise ValidationError('Username cannot contain @')

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def is_authenticated(self):
        return self.is_logged_in()

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

    @staticmethod
    def find_by_username(username: str) -> 'ChirperUser':
        return ChirperUser.objects.get(user__username=username)

    @staticmethod
    def find_by_key(key: str) -> 'ChirperUser':
        return ChirperUser.objects.get(session__key=key)

    @staticmethod
    def username_exists(username: str) -> bool:
        return ChirperUser.objects.filter(user__username=username).exists()

    def chirp(self, message):
        '`ChirperUser.chirp` will create a new chirp with the provided message and `self` as the author'
        return Chirp.objects.create(author=self, message=message)

    def feed(self) -> QuerySet:
        '`ChirperUser.feed` returns a queryset representing all `Chirp`s that belong to `self`\'s feed.'
        return (self.chirp_set.all() |
                self.chirping_at_set.all()).order_by('date')

    def login(self):
        if self.is_logged_in():
            self.logout()
        Session.create(self)

    def is_logged_in(self):
        try:
            return self.session.id is not None
        except Session.DoesNotExist:
            return False

    def logout(self):
        if self.is_logged_in():
            self.session.delete()


class Chirp(models.Model):
    message = models.CharField(max_length=280)
    author = models.ForeignKey(ChirperUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    chirping_at = models.ManyToManyField(
        ChirperUser, related_name='chirping_at_set')

    def save(self, *args, **kwargs):
        super(Chirp, self).save(*args, **kwargs)
        usernames = [w[1:] for w in self.message.split() if w.startswith('@')]
        users = ChirperUser.objects.filter(user__username__in=usernames)
        for user in users:
            self.chirping_at.add(user)

    def __str__(self):
        return '{} ({}): {}'.format(self.author.username, self.date,
                                    self.message)


class Session(models.Model):
    chirperuser = models.OneToOneField(ChirperUser, on_delete=models.CASCADE)
    key = models.CharField(max_length=40)

    @staticmethod
    def create(chirperuser):
        chirperuser.session = Session.objects.create(
            chirperuser=chirperuser,
            key=secrets.token_hex(20), )

        return chirperuser.session

    @staticmethod
    def delete_with_key(key):
        Session.objects.get(key=key).chirperuser.logout()
