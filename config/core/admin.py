from django.contrib import admin
from .models import Empresa, Empleado, Ingreso

admin.site.register(Empresa)
admin.site.register(Empleado)
admin.site.register(Ingreso)
