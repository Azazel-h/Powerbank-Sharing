from django.test import TestCase, Client
from django.contrib.auth.models import User
from sharing.models import Powerbank, Profile, Share, Order
from sharing.views.helpers import get_profile, get_last_order, \
     remaining_min, fail_order, powerbank_percentage


class TestHelpers(TestCase):
    def setUp(self):
        """
        Начальные параметры
        :return:
        """
        user = User.objects.create_user(username='Azazel',
                                        email='azazel@ya.ru',
                                        password='23452345')
        p1 = Profile.objects.create(user=user, name='azazel')

        superuser = User.objects.create_superuser(username='root',
                                                  email='root@ya.ru',
                                                  password='rootpass')
        p2 = Profile.objects.create(user=superuser, name='root')

        pb = Powerbank.objects.create(capacity=1000, location=1, status='free')

    def test_powerbank_percentage(self):
        self.assertEqual(1, powerbank_percentage())

    def test_get_profile(self):
        self.assertEqual(get_profile(self.user), self.p1)
