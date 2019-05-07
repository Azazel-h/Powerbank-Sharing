from django.test import TestCase, Client
from django.contrib.auth.models import User
from sharing.models import Share, Profile, Order, PaymentPlan

class TestCheat(TestCase):
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

    def test_make_verified(self):
        admin = Client()
        admin.login(username='root', password='rootpass')
        response = admin.post('/debug/make_verified')
        profile = Profile.objects.get(id=2)
        self.assertEqual(profile.passport_status, 'success')
        self.assertEqual(profile.active_mail, True)
        self.assertEqual(profile.name, 'Sbeve Sbeve')

    def test_make_verified_validation(self):
        user = Client()
        user.login(username='xenon', password='23452345')
        response = user.post('/debug/make_verified')
        self.assertEqual(302, response.status_code)

    def test_display_points(self):
        admin = Client()
        admin.login(username='root', password='rootpass')
        response = admin.post('/debug/display_points')
        
        self.assertEqual(200, response.status_code)

    def test_display_points_validation(self):
        user = Client()
        user.login(username='xenon', password='23452345')
        response = user.post('/debug/display_points')
        self.assertEqual(302, response.status_code)

    def test_display_orders(self):
        admin = Client()
        admin.login(username='root', password='rootpass')
        response = admin.post('/debug/display_orders')
        self.assertEqual(response.context['orders'].count(), 0)

    def test_display_orders_validation(self):
        user = Client()
        user.login(username='xenon', password='23452345')
        response = user.post('/debug/display_orders')
        self.assertEqual(302, response.status_code)

    def test_display_plans(self):
        admin = Client()
        admin.login(username='root', password='rootpass')
        response = admin.post('/debug/display_plans')
        self.assertEqual(response.context['plans'].count(), 0)

    def test_display_plans_validation(self):
        user = Client()
        user.login(username='xenon', password='23452345')
        response = user.post('/debug/display_plans')
        self.assertEqual(302, response.status_code)

    def test_reset_orders(self):
        admin = Client()
        admin.login(username='root', password='rootpass')
        Order.objects.create(progress='applied')
        response = admin.post('/debug/reset_orders')
        self.assertEqual(Order.objects.all().count(), 0)




