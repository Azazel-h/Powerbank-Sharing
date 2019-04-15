from django.db import models
from django.contrib.auth.models import User


class Powerbank(models.Model):
    """
    status: free     - заряжен и готов к использованию
            ordered  - забронирован, но не используется
            occupied - используется кем-то
            charging - заряжается
    """
    code = models.CharField(max_length=256)
    capacity = models.IntegerField()
    location = models.IntegerField()
    status = models.CharField(max_length=256)

    @staticmethod
    def get_all():
        return Powerbank.objects.all()


class Profile(models.Model):
    """
    passport_status: empty - фотография еще не отправлена (значение по умолчанию)
                     checking - фотография отправлена, но проходит проверку
                     success - фотография одобрена, проверка прошла успешно
                     fail - фотография не одобрена, не прошла проверку

    session_status: inactive - сессия даже не думает быть начатой (по умолчанию)
                    on_begin - скан кода произошел, сессия сейчас начнется
                    active   - сессия активна
                    on_end   - скан кода произошел, сессия сейчас закончится
                    fail     - ошибка в процессе сессии

    wallets: string, в котором перечислены id кошельков из модели Wallet
    payment_plans: string, в котором перечислены id доступных планов оплаты из модели PaymentPlan
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=512,  null=True)
    active_mail = models.BooleanField(default=False)
    photo = models.FileField(upload_to='users/')
    passport = models.FileField(upload_to='passports/')
    passport_status = models.CharField(max_length=216, default='empty')
    wallets = models.CharField(max_length=512, default='')
    payment_plans = models.CharField(max_length=512, default='')

    hold = models.ForeignKey(Powerbank, on_delete=models.SET_NULL, null=True)

    @staticmethod
    def get_progress_complete_account(user):
        default = ['', False, '', '']
        profile = Profile.objects.get(user=user)
        d = {
            'name': profile.name,
            'active_mail': profile.active_mail,
            'photo': profile.photo,
            'passport': profile.passport
        }
        res = [x for x in list(d.values()) if x not in default]
        return {
            'num-completed': len(res),
            'percentage': str((100 * len(res) // len(default))) + '%'
        }


class Share(models.Model):
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

class Wallet(models.Model):
    """
    status: active - кошелёк в нормальном состоянии
            suspended - заморожен (есть задолженность, по её устранению кошелёк снова активен)
            blocked - заблокирован (нельзя восстановить этот кошелёк)
            infinite - бесконечный 

    payment_method: promo - деньги даны в подарок
                    banking - банковская карта
                    cash - наличные
                    crypto - крипта
                    other - другое (хммм)
    """
    balance = models.FloatField(default=0.0)
    status = models.CharField(max_length=128, default='active')
    payment_method = models.CharField(max_length=128, default='promo')

class PaymentPlan(models.Model):
    """
    payment_type: perminute - поминутная оплата
                  instant - мгновенная
    """
    name = models.CharField(max_length=128, default='Обычный')
    description = models.CharField(max_length=512, default='Самый обычный тариф.')
    payment_type = models.CharField(max_length=128, default='perminute')
    cost = models.FloatField(default=0.0)