"""
Модули:
    - django:
        - db
        - contrib.auth.models
"""
from django.db import models
from django.contrib.auth.models import User


class Powerbank(models.Model):
    """
    status: free     - заряжен и готов к использованию
            ordered  - забронирован, но не используется
            occupied - используется кем-то
            charging - заряжается
    """
    capacity = models.IntegerField()
    location = models.IntegerField()
    status = models.CharField(max_length=256)

    @staticmethod
    def get_all():
        """
        Получить все объекты
        :return:
        """
        return Powerbank.objects.all()


class PaymentPlan(models.Model):
    """
    cost - стоимость подписки
    duration - длительность в днях

    class Wallet(models.Model):
    '''
    status:
    active - кошелёк в нормальном состоянии
    suspended - заморожен
    (есть задолженность, по её устранению кошелёк снова активен)
    blocked - заблокирован
    (нельзя восстановить этот кошелёк)
    infinite - бесконечный

    payment_method:
    promo - деньги даны в подарок
    banking - банковская карта
    cash - наличные
    crypto - крипта
    other - другое (хммм)
    '''
    name = models.CharField(max_length=128, default='Кошелёк')
    balance = models.FloatField(default=0.0)
    status = models.CharField(max_length=128, default='active')
    payment_method = models.CharField(max_length=128, default='promo')
    """
    name = models.CharField(max_length=128, default='Обычная')
    description = models.CharField(max_length=512,
                                   default='Самая обычная подписка.')
    cost = models.FloatField(default=0.0)
    duration = models.IntegerField(default=7)


class Profile(models.Model):
    """
    passport_status:
    empty - фотография еще не отправлена (значение по умолчанию)
    checking - фотография отправлена, но проходит проверку
    success - фотография одобрена, проверка прошла успешно
    fail - фотография не одобрена, не прошла проверку

    payment_plan - подписка пользователя
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=512, null=True)
    active_mail = models.BooleanField(default=False)
    photo = models.FileField(upload_to='users/')
    passport = models.FileField(upload_to='passports/')
    passport_status = models.CharField(max_length=216, default='empty')
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL,
                                     null=True)
    payment_plan_activation_time = models.DateTimeField(auto_now_add=True)
    hold = models.ForeignKey(Powerbank, on_delete=models.SET_NULL, null=True)

    @staticmethod
    def get_progress_complete_account(user):
        """
        Функция проверки заполненности профиля[%]
        :param user:
        :return:
        """
        default = ['', False, '', '']
        profile = Profile.objects.get(user=user)
        date = {
            'name': profile.name,
            'active_mail': profile.active_mail,
            'photo': profile.photo,
            'passport': profile.passport
        }
        res = [x for x in list(date.values()) if x not in default]
        return {
            'num-completed': len(res),
            'percentage': (100 * len(res) // len(default))
        }


class Share(models.Model):
    """
    Модель станции powerbank'ов:
        - title:
        - address:
        - crds_lot:
        - crds_lat:
        - time:
        - qrcode:
        - ip:
        - free_pbs:
    """
    title = models.CharField(max_length=256)
    address = models.CharField(max_length=512)
    crds_lot = models.FloatField()
    crds_lat = models.FloatField()
    time = models.TimeField(auto_now_add=True)
    qrcode = models.CharField(max_length=512, default='Hello, world!')
    ip = models.CharField(max_length=256, default='127.0.0.1')
    free_pbs = models.IntegerField(default=False)

    @staticmethod
    def get_all():
        """
        Получить все объекты
        :return:
        """
        return Share.objects.all()


class Order(models.Model):
    """
    order_type: hold  - отложенный заказ (бронирование)
                immediate - немедленный заказ (получить пб прямо сейчас)

    progress: created - заказ только что сделан
              applied - заказ выполняется (пб у юзера)
              cancelled - заказ отменен
              blocked - заказ заблокирован
              failed - заказ провален (истекло время брони)
              ended - заказ завершен

    reservation_time: время бронирования в минутах
    """
    share = models.ForeignKey(Share, on_delete=models.SET_NULL, null=True)
    pb = models.ForeignKey(Powerbank, on_delete=models.SET_NULL, null=True)
    order_type = models.CharField(max_length=128, default='hold')
    timestamp = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    progress = models.CharField(max_length=128, default='created')
    reservation_time = models.IntegerField(default=15)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL,
                                     null=True)
    end_share = models.ForeignKey(Share, on_delete=models.SET_NULL,
                                  null=True,
                                  related_name='end_share')
    end_timestamp = models.DateTimeField(auto_now_add=True)


class PollQuery(models.Model):
    """
    share_id: ID автомата

    timestamp: дата-время запроса

    status: pending - запрос ожидает выполнения
            done - запрос выполнен
    """
    share_id = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=128, default='pending')
