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
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=512,  null=True)
    active_mail = models.BooleanField(default=False)
    photo = models.FileField(upload_to='users/')
    passport = models.FileField(upload_to='passports/')
    passport_status = models.CharField(max_length=216, default='empty')
    session_status = models.CharField(max_length=256, default='inactive')

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
    has_pb = models.BooleanField(default=False)

    @staticmethod
    def get_all():
        return Share.objects.all()

class Order(models.Model):
    """
    order_type: hold  - отложенный заказ (бронирование)
                immediate - немедленный заказ (получить пб прямо сейчас)
    """
    share = models.ForeignKey(Share, on_delete=models.SET_NULL, null=True)
    pb = models.ForeignKey(Powerbank, on_delete=models.SET_NULL, null=True)
    order_type = models.CharField(max_length=128, default='hold')
    timestamp = models.TimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    