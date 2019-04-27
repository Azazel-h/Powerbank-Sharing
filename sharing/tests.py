from django.test import TestCase, Client
from django.contrib.auth.models import User
from sharing.models import Profile


class TestUser(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='koritsa', email='test@ya.ru', password='12341234')
        Profile.objects.create(user=user, name='koritsa')

    def test_signup_user(self):
        c = Client()
        data = {
            'username': 'Alexander',
            'email': '123@gmail.com',
            'password1': '12341234',
            'password2': '12341234'
        }
        response = c.post('/accounts/signup', data)
        user = User.objects.get(id=2)
        profile = Profile.objects.get(id=2)

        self.assertEqual('Alexander', user.username)
        self.assertEqual(user, profile.user)

    def test_change_name(self):
        c = Client()
        r = c.login(username='koritsa', password='12341234')
        data = {
            'name': 'Sashka'
        }
        response = c.post('/change/name', data)
        profile = Profile.objects.get(id=1)
        self.assertEqual('Sashka', profile.name)

    def test_change_email(self):
        c = Client()
        c.login(username='koritsa', password='12341234')
        data = {
            'new_email1': 'asd@mail.ru',
            'new_email2': 'asd@mail.ru'
        }
        response = c.post('/change/email', data)
        user = User.objects.get(id=1)

        self.assertEqual('asd@mail.ru', user.email)

    def test_change_password(self):
        c = Client()
        c.login(username='koritsa', password='12341234')
        data = {
            'old_password': '12341234',
            'new_password1': '12345678',
            'new_password2': '12345678'
        }
        response = c.post('/change/pass', data)
        res = c.login(username='koritsa', password='12345678')
        self.assertEqual(res, True)
