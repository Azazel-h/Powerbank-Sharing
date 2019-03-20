from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=512)
    active_mail = models.BooleanField(default=False)
    photo = models.CharField(max_length=512)
    status = models.CharField(max_length=512, default='')


class Share(models.Model):
    title = models.CharField(max_length=256)
    address = models.CharField(max_length=512)
    crds_lot = models.FloatField()
    crds_lat = models.FloatField()
    time = models.TimeField(auto_now_add=True)

    @staticmethod
    def get_all():
        return Share.objects.all()
