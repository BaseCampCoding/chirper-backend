import json

from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from app.models import ChirperUser, Session


def identity(x):
    return x


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

    def test_username_cannot_have_at_sign(self):
        with self.assertRaises(ValidationError):
            ChirperUser.signup('Nate', '@natec425', 'foo@example.com',
                               'badpass')

    def test_chirper_user_can_chirp(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        chirp = chirper.chirp("Hello World")

        self.assertEqual(chirp.author, chirper)
        self.assertEqual(chirp.message, "Hello World")

    def test_feed_with_chirps(self):

        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        hello_chirp = chirper.chirp("Hello World")
        game_over_chirp = chirper.chirp("Game Over")

        self.assertQuerysetEqual(
            chirper.feed(), [game_over_chirp, hello_chirp], transform=identity)

    def test_feed_with_chirping_at(self):
        nate = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                  'badpass')

        not_nate = ChirperUser.signup('Not Nate', 'not_nate', 'foo@example.com',
                                      'badpass')

        hey_chirp = nate.chirp('Hey @not_nate')

        self.assertQuerysetEqual(nate.feed(), [hey_chirp], transform=identity)
        self.assertQuerysetEqual(
            not_nate.feed(), [hey_chirp], transform=identity)

    def test_username_does_exist(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        self.assertTrue(ChirperUser.username_exists('natec425'))
        self.assertFalse(ChirperUser.username_exists('notnate'))

    def test_login_logout(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        self.assertFalse(chirper.is_logged_in())
        chirper.login()
        self.assertTrue(chirper.is_logged_in())
        chirper.logout()
        self.assertFalse(chirper.is_logged_in())

    def test_login_logout_multiple_times(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        for _ in range(5):
            self.assertFalse(chirper.is_logged_in())
            chirper.login()
            self.assertTrue(chirper.is_logged_in())
            chirper.logout()

    def test_chirp_chirping_at(self):
        nate = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                  'badpass')

        not_nate = ChirperUser.signup('Not Nate', 'not_nate', 'foo@example.com',
                                      'badpass')

        chirp = nate.chirp('Hello @not_nate @not_nate @not_nate')

        self.assertQuerysetEqual(
            chirp.chirping_at.all(), [not_nate], transform=identity)

        self.assertQuerysetEqual(not_nate.feed(), [chirp], transform=identity)

        self.assertQuerysetEqual(nate.feed(), [chirp], transform=identity)


class TestViews(TestCase):
    def test_successful_signup(self):
        response = self.client.post(
            '/api/signup/',
            json.dumps({
                'name': 'Nate',
                'username': 'natec425',
                'email': 'foo@example.com',
                'password': 'badpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            'key',
            json.loads(response.content.decode('utf-8')), )

    def test_missing_data_signup(self):
        response = self.client.post(
            '/api/signup/',
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
            '/api/signup/',
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
            '/api/signup/', 'this', content_type='text/plain')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'MALFORMED_REQUEST'})

    def test_sending_with_bad_email_signup(self):
        response = self.client.post(
            '/api/signup/',
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

    def test_empty_feed(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')
        response = self.client.get('/api/natec425/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'chirper': {
                'name': 'Nate',
                'username': 'natec425',
                'joined': {
                    'month': chirper.joined.month,
                    'year': chirper.joined.year
                },
                'description': '',
                'location': '',
                'website': ''
            },
            'chirps': []
        })

    def test_nonempty_feed(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')
        hello_chirp = chirper.chirp("Hello")
        world_chirp = chirper.chirp("World")

        response = self.client.get('/api/natec425/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'chirper': {
                'name': 'Nate',
                'username': 'natec425',
                'joined': {
                    'month': chirper.joined.month,
                    'year': chirper.joined.year
                },
                'description': '',
                'location': '',
                'website': ''
            },
            'chirps': [{
                'author': {
                    'name': chirper.name,
                    'username': chirper.username
                },
                'date': {
                    'month': world_chirp.date.month,
                    'day': world_chirp.date.day,
                    'year': world_chirp.date.year
                },
                'message': world_chirp.message
            }, {
                'author': {
                    'name': chirper.name,
                    'username': chirper.username
                },
                'date': {
                    'month': hello_chirp.date.month,
                    'day': hello_chirp.date.day,
                    'year': hello_chirp.date.year
                },
                'message': hello_chirp.message
            }]
        })

    def test_feed_for_unknown_user_404s(self):
        response = self.client.get('/api/natec425/')
        self.assertEqual(response.status_code, 404)

    def test_successful_login(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        response = self.client.post(
            '/api/login/',
            json.dumps({
                'username': 'natec425',
                'password': 'badpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('key', json.loads(response.content.decode('utf-8')))
        self.assertTrue(chirper.is_logged_in())

    def test_invalid_password_login(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        response = self.client.post(
            '/api/login/',
            json.dumps({
                'username': 'natec425',
                'password': 'incorrectpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
                         {'error': 'INVALID_USERNAME_PASSWORD'})

        self.assertFalse(chirper.is_logged_in())

    def test_login_for_nonexistent_user(self):
        response = self.client.post(
            '/api/login/',
            json.dumps({
                'username': 'natec425',
                'password': 'badpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
                         {'error': 'INVALID_USERNAME_PASSWORD'})

    def test_login_with_bad_payload(self):
        response = self.client.post(
            '/api/login/', 'this', content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_login_with_bad_data(self):
        response = self.client.post(
            '/api/login/',
            json.dumps({
                'username': 'foo'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {'error': 'INVALID_DATA'})

    def test_login_then_logout(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        response = self.client.post(
            '/api/login/',
            json.dumps({
                'username': 'natec425',
                'password': 'badpass'
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(chirper.is_logged_in())

        response = self.client.post(
            '/api/logout/',
            response.content.decode('utf-8'),
            content_type='application/json')

        chirper.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(chirper.is_logged_in())

    def test_username_exists(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        response = self.client.get('/api/username_exists/natec425/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'exists': True})

    def test_username_doesnt_exists(self):
        response = self.client.get('/api/username_exists/natec425/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'exists': False})

    def test_chirp_requires_login(self):
        response = self.client.post(
            '/api/chirp/',
            json.dumps({
                'message': 'Hello World'
            }),
            content_type='application/json', )

        self.assertEqual(response.status_code, 401)

    def test_chirp_with_logged_in_user(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        chirper.login()

        response = self.client.post(
            '/api/chirp/',
            json.dumps({
                'key': chirper.session.key,
                'message': 'Hello World'
            }),
            content_type='application/json', )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(chirper.chirp_set.count(), 1)
        self.assertEqual(chirper.chirp_set.first().message, 'Hello World')

    def test_chirp_with_malformed_payload(self):

        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        chirper.login()

        response = self.client.post(
            '/api/chirp/',
            'this',
            content_type='text/plain', )

        self.assertEqual(response.status_code, 400)

    def test_chirp_without_message(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        chirper.login()

        response = self.client.post(
            '/api/chirp/',
            json.dumps({
                'key': chirper.session.key
            }),
            content_type='application/json', )

        self.assertEqual(response.status_code, 422)
