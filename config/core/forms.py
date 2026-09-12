from django import forms
from .models import Ingreso

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = [
            'empresa',
            'empleado',
            'puesto',
            'nombre_completo',
            'curp',
            'telefono',
            'fecha_entrevista',
            'fecha_ingreso',
            'monto_estimado',
        ]
        widgets = {
            'fecha_entrevista': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }