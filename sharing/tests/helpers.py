"""
   Тест хэлперов
"""
from django.test import TestCase
from django.contrib.auth.models import User
from sharing.models import Profile
from sharing.views.helpers import get_profile, \
     powerbank_percentage


class TestHelpers(TestCase):
    """
        Начальные параметры
        :return:
    """
    def setUp(self):
        """
        Начальные параметры
        :return:
        """
        self.user = User.objects.create_user(username='Azazel',
                                             email='azazel@ya.ru',
                                             password='23452345')
        self.p_1 = Profile.objects.create(user=self.user,
                                          name='azazel')

    def test_powerbank_percentage(self):
        """
        Начальные параметры
        :return:
        """
        self.assertEqual(1, powerbank_percentage())

    def test_get_profile(self):
        """
        Начальные параметры
        :return:
        """
        self.assertEqual(get_profile(self.user), self.p_1)
