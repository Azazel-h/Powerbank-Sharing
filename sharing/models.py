from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    passport_status: empty - фотография еще не отправлена (значение по умолчанию)
                     checking - фотография отправлена, но проходит проверку
                     success - фотография одобрена, проверка прошла успешно
                     fail - фотография не одобрена, не прошла проверку
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=512,  null=True)
    active_mail = models.BooleanField(default=False)
    photo = models.FileField(upload_to='users/')
    passport = models.FileField(upload_to='passports/')
    passport_status = models.CharField(max_length=216, default='empty')

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

    @staticmethod
    def get_all():
        return Share.objects.all()


class Powerbank(models.Model):
    code = models.CharField(max_length=256)
    value = models.IntegerField()
    location = models.IntegerField()
    status = models.CharField(max_length=256)

    @staticmethod
    def get_all():
        return Powerbank.objects.all()
