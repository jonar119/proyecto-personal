from django.contrib import admin
from django.urls import path
from core.views import (
    registrar_ingreso,
    lista_ingresos,
    reportes,
    CustomLoginView,
    cerrar_sesion,
    generar_pdf,
    importar_csv,
    dashboard,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('registrar/', registrar_ingreso, name='registrar_ingreso'),
    path('ingresos/', lista_ingresos, name='lista_ingresos'),
    path('reportes/', reportes, name='reportes'),
    path('pdf/', generar_pdf, name='generar_pdf'),
    path('importar-csv/', importar_csv, name='importar_csv'),
]