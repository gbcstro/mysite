from django.db import models

class Cargo(models.Model):
    num_box = models.IntegerField(null=True)
    capacity = models.IntegerField(null=True)
    ini_rate = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    cargo_type = models.CharField(null=True, max_length=100)

    def __str__(self):
        return self.cargo_type

class cargoList(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, null=True)
    box = models.IntegerField(null=True)
    description = models.CharField(max_length=255, blank=True)
    height = models.FloatField(null=True)
    length = models.FloatField(null=True)
    width = models.FloatField(null=True)
    weight = models.FloatField(null=True)
    cbm = models.FloatField(null=True)
    chargeable_weight = models.FloatField(null=True)
    profit = models.FloatField(null=True)

    def __str__(self):
        return self.box