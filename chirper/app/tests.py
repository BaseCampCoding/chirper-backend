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


class TestViews(TestCase):
    def test_successful_signup(self):
        response = self.client.post(
            '/signup/',
            json.dumps({
                'name': 'Nate',
                'username': 'natec425',
                'email': 'foo@example.com',
                'password': 'badpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content.decode('utf-8'), {})

    def test_missing_data_signup(self):
        response = self.client.post(
            '/signup/',
            json.dumps({
                'username': 'natec425',
                'email': 'foo@example.com',
                'password': 'badpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {
            'error': 'INVALID_DATA',
            'errors': {
                'name': ['This field cannot be null.']
            }
        })

    def test_duplicate_username_signup(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        response = self.client.post(
            '/signup/',
            json.dumps({
                'name': 'Not Nate',
                'username': 'natec425',
                'email': 'bar@example.com',
                'password': 'badpass2'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {
            'error': 'INVALID_DATA',
            'errors': {
                'username': ['A user with that username already exists.']
            }
        })

    def test_sending_malformed_json_signup(self):
        response = self.client.post(
            '/signup/', 'this', content_type='text/plain')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'MALFORMED_REQUEST'})

    def test_sending_with_bad_email_signup(self):
        response = self.client.post(
            '/signup/',
            json.dumps({
                'name': 'nate',
                'username': 'natec425',
                'email': 'bar',
                'password': 'badpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {
            'error': 'INVALID_DATA',
            'errors': {
                'email': ['Enter a valid email address.']
            }
        })
