from django.test import TestCase, Client
from django.contrib.auth.models import User
from sharing.models import Profile


class TestUser(TestCase):
    def test_signup_user(self):
        c = Client()
        data = {
            'username': 'Alexander',
            'email': '123@gmail.com',
            'password1': '12341234',
            'password2': '12341234'
        }
        response = c.post('/accounts/signup', data)
        user = User.objects.get(id=1)
        profile = Profile.objects.get(id=1)

        self.assertEqual('Alexander', user.username)
        self.assertEqual(user, profile.user)
