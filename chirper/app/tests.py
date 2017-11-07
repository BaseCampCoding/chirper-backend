from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from app.models import ChirperUser
from django.contrib.auth.models import User
import json


class TestModels(TestCase):
    def test_can_sign_up(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        assert chirper.name == 'Nate'
        assert chirper.username == 'natec425'
        assert chirper.email == 'foo@example.com'

    def test_cannot_signup_two_users_with_same_username(self):
        ChirperUser.signup('Nate', 'natec425', 'foo@example.com', 'badpass')

        with self.assertRaises(ValidationError):
            ChirperUser.signup('Not Nate', 'natec425', 'bar@example.com',
                               'badpass2')

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(ChirperUser.objects.count(), 1)

    def test_cannot_signup_user_with_short_name(self):
        with self.assertRaises(ValidationError):
            ChirperUser.signup('N', 'natec425', 'foo@example.com', 'badpass')

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(ChirperUser.objects.count(), 0)

    def test_cannot_signup_user_with_long_name(self):
        with self.assertRaises(ValidationError):
            ChirperUser.signup('N' * 200, 'natec425', 'foo@example.com',
                               'badpass')

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(ChirperUser.objects.count(), 0)

    def test_chirper_user_can_chirp(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        chirp = chirper.chirp("Hello World")

        self.assertEqual(chirp.author, chirper)
        self.assertEqual(chirp.message, "Hello World")
