from django.contrib import admin

from cargoloading.models import Cargo, cargoList

# Register your models here.
admin.site.register(Cargo)
admin.site.register(cargoList)
