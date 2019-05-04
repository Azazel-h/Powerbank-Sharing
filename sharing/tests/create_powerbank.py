from django.test import TestCase, Client
from django.contrib.auth.models import User
from sharing.models import Profile

class TestAddPowerbankSharing(TestCase):
    """
    Класс для тестирования функции add_powerbank_sharing
    """
    def setUp(self):
        """
        Начальные параметры
        :return:
        """
        user = User.objects.create_user(username='xenon',
                                        email='test@ya.ru',
                                        password='23452345')
        Profile.objects.create(user=user, name='xenon')

        superuser = User.objects.create_superuser(username='root',
                                                  email='root@ya.ru',
                                                  password='rootpass')
        Profile.objects.create(user=superuser, name='root')

    def test_login_user_page_add_powerbank_sharing(self):
        """
        Вход на страницу с аккаунта пользователя
        :return:
        """
        client = Client()

        client.login(username='xenon', password='23452345')

        response = client.get('/sharing/add')

        self.assertEqual(302, response.status_code)

    def test_login_admin_page_add_powerbank_sharing(self):
        """
        Вход на страницу с аккаунта администратора
        :return:
        """
        admin = Client()

        admin.login(username='root', password='rootpass')

        response = admin.get('/sharing/add')

        self.assertEqual(200, response.status_code)

    def test_add_powerbank_sharing(self):
        """
        Добавление новой станции
        :return:
        """
        admin = Client()

        admin.login(username='root', password='rootpass')

        data = {
            'title': 'Main',
            'address': 'Moscow, Russia',
            'qrcode': 'Hello, world!',
            'ip': '127.0.0.1',
            'crds': '[50.450441,30.52355]'
        }

        response = admin.post('/sharing/add', data)

        self.assertEqual('OK', response.reason_phrase)


class TestAddPowerbank(TestCase):
    """
    Класс для тестирования функции add_pb
    """
    def setUp(self):
        """
        Начальные параметры
        :return:
        """
        user = User.objects.create_user(username='xenon',
                                        email='test@ya.ru',
                                        password='23452345')
        Profile.objects.create(user=user, name='xenon')

        superuser = User.objects.create_superuser(username='root',
                                                  email='root@ya.ru',
                                                  password='rootpass')
        Profile.objects.create(user=superuser, name='root')

    def test_login_user_page_add_pb(self):
        """
        Вход на страницу с аккаунта пользователя
        :return:
        """
        client = Client()

        client.login(username='xenon', password='23452345')

        response = client.get('/sharing/add_pb')

        self.assertEqual(302, response.status_code)

    def test_login_admin_page_add_pb(self):
        """
        Вход на страницу с аккаунта администратора
        :return:
        """
        admin = Client()

        admin.login(username='root', password='rootpass')

        response = admin.get('/sharing/add_pb')

        self.assertEqual(200, response.status_code)

    def test_add_pb(self):
        """
        Добавление новой станции
        :return:
        """
        admin = Client()

        admin.login(username='root', password='rootpass')

        data = {
            'location': 'Main',
            'capacity': 'Moscow, Russia',
        }

        response = admin.post('/sharing/add', data)

        self.assertEqual('OK', response.reason_phrase)