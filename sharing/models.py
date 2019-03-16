from django.db import models


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
    location = models.CharField(max_length=512)
    status = models.CharField(max_length=256)

    @staticmethod
    def get_all():
        return Powerbank.objects.all()
