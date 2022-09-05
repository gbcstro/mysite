from django.db import models


class CargoTable(models.Model):
    box_num = models.PositiveIntegerField()
    description = models.TextField()
    height = models.FloatField()
    width = models.FloatField()
    weight = models.FloatField()
    length = models.FloatField()
    CBM = models.FloatField()
    chargeable_weight = models.FloatField()
    cost = models.FloatField()

    def __str__(self):
        return self.box_num

 




