from django.test import TestCase
from django.db.utils import IntegrityError
from app.models import ChirperUser


class TestChirperUserSignup(TestCase):
    def test_can_sign_up(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        assert chirper.name == 'Nate'
        assert chirper.username == 'natec425'
        assert chirper.email == 'foo@example.com'

    def test_cannot_create_two_users_with_same_username(self):
        ChirperUser.signup('Nate', 'natec425', 'foo@example.com', 'badpass')

        with self.assertRaises(IntegrityError):
            ChirperUser.signup('Not Nate', 'natec425', 'bar@example.com',
                               'badpass2')
