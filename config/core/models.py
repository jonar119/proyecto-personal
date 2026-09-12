from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    monto_nomina = models.DecimalField(max_digits=10, decimal_places=2)
    monto_factura = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre


class Ingreso(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    capturado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    puesto = models.CharField(max_length=100)
    nombre_completo = models.CharField(max_length=150)
    curp = models.CharField(max_length=18)
    telefono = models.CharField(max_length=15)

    fecha_entrevista = models.DateField()
    fecha_ingreso = models.DateField()

    monto_estimado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre_completo
