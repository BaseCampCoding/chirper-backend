from django.test import TestCase
from app.models import ChirperUser


class TestChirperUserSignup(TestCase):
    def test_can_sign_up(self):
        chirper = ChirperUser.signup('Nate', 'natec425', 'foo@example.com',
                                     'badpass')

        assert chirper.name == 'Nate'
        assert chirper.username == 'natec425'
        assert chirper.email == 'foo@example.com'
