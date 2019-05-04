from django.test import TestCase, Client
from django.contrib.auth.models import User
from sharing.models import Profile

class TestUser(TestCase):
    """
    Класс для тестирования системы пользователей
    """
    def setUp(self) -> None:
        """
        Установочная функция
        :return:
        """
        user = User.objects.create_user(username='koritsa',
                                        email='test@ya.ru',
                                        password='12341234')
        Profile.objects.create(user=user, name='koritsa')

    def test_signup_user(self):
        """
        Тест регистрации пользователя
        :return:
        """
        client = Client()
        data = {
            'username': 'Alexander',
            'email': '123@gmail.com',
            'password1': '12341234',
            'password2': '12341234'
        }
        client.post('/accounts/signup', data)
        user = User.objects.get(id=2)
        profile = Profile.objects.get(id=2)

        self.assertEqual('Alexander', user.username)
        self.assertEqual(user, profile.user)

    def test_change_name(self):
        """
        Тест смены имени пользователя
        :return:
        """
        client = Client()
        client.login(username='koritsa', password='12341234')
        data = {
            'name': 'Sashka'
        }
        client.post('/change/name', data)
        profile = Profile.objects.get(id=1)
        self.assertEqual('Sashka', profile.name)

    def test_change_email(self):
        """
        Тест смены электронной почты
        :return:
        """
        client = Client()
        client.login(username='koritsa', password='12341234')
        data = {
            'new_email1': 'asd@mail.ru',
            'new_email2': 'asd@mail.ru'
        }
        client.post('/change/email', data)
        user = User.objects.get(id=1)

        self.assertEqual('asd@mail.ru', user.email)

    def test_change_password(self):
        """
        Тест смены пароля
        :return:
        """
        client = Client()
        client.login(username='koritsa', password='12341234')
        data = {
            'old_password': '12341234',
            'new_password1': '12345678',
            'new_password2': '12345678'
        }
        client.post('/change/pass', data)
        res = client.login(username='koritsa', password='12345678')
        self.assertEqual(res, True)
