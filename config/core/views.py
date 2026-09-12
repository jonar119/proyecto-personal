import csv
import io
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .forms import IngresoForm
from .models import Ingreso, Empresa, Empleado


class CustomLoginView(LoginView):
    template_name = 'core/login.html'


def cerrar_sesion(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')


@login_required
def registrar_ingreso(request):
    if request.method == 'POST':
        form = IngresoForm(request.POST)
        if form.is_valid():
            ingreso = form.save(commit=False)
            ingreso.capturado_por = request.user
            ingreso.save()
            return redirect('registrar_ingreso')
    else:
        form = IngresoForm()

    mostrar_costos = False
    if (
        request.user.is_superuser
        or request.user.groups.filter(name='nomina').exists()
        or request.user.groups.filter(name='facturacion').exists()
    ):
        mostrar_costos = True

    ingresos = Ingreso.objects.filter(capturado_por=request.user).order_by('-id')[:10]

    total_ingresos = ingresos.count()
    total_nomina = 0
    total_factura = 0

    for ingreso in ingresos:
        total_nomina += ingreso.empresa.monto_nomina
        total_factura += ingreso.empresa.monto_factura

    return render(request, 'core/registrar_ingreso.html', {
        'form': form,
        'ingresos': ingresos,
        'mostrar_costos': mostrar_costos,
        'total_ingresos': total_ingresos,
        'total_nomina': total_nomina,
        'total_factura': total_factura,
    })


@login_required
def lista_ingresos(request):
    mostrar_costos = False
    if (
        request.user.is_superuser
        or request.user.groups.filter(name='nomina').exists()
        or request.user.groups.filter(name='facturacion').exists()
    ):
        mostrar_costos = True

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    ingresos = Ingreso.objects.all().order_by('-fecha_ingreso', '-id')

    if fecha_inicio and fecha_fin:
        ingresos = ingresos.filter(fecha_ingreso__range=[fecha_inicio, fecha_fin])

    total_ingresos = ingresos.count()
    total_nomina = 0
    total_factura = 0

    for ingreso in ingresos:
        total_nomina += ingreso.empresa.monto_nomina
        total_factura += ingreso.empresa.monto_factura

    return render(request, 'core/lista_ingresos.html', {
        'ingresos': ingresos,
        'mostrar_costos': mostrar_costos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_ingresos': total_ingresos,
        'total_nomina': total_nomina,
        'total_factura': total_factura,
    })


@login_required
def reportes(request):
    mostrar_costos = False
    if (
        request.user.is_superuser
        or request.user.groups.filter(name='nomina').exists()
        or request.user.groups.filter(name='facturacion').exists()
    ):
        mostrar_costos = True

    return render(request, 'core/reportes.html', {
        'mostrar_costos': mostrar_costos,
    })


@login_required
def generar_pdf(request):
    mostrar_costos = False
    if (
        request.user.is_superuser
        or request.user.groups.filter(name='nomina').exists()
        or request.user.groups.filter(name='facturacion').exists()
    ):
        mostrar_costos = True

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo_reporte = request.GET.get('tipo_reporte', 'general')

    ingresos = Ingreso.objects.all().order_by('-fecha_ingreso')

    if fecha_inicio and fecha_fin:
        ingresos = ingresos.filter(fecha_ingreso__range=[fecha_inicio, fecha_fin])

    total_ingresos = ingresos.count()
    total_nomina = 0
    total_factura = 0

    for ingreso in ingresos:
        total_nomina += ingreso.empresa.monto_nomina
        total_factura += ingreso.empresa.monto_factura

    template = get_template('core/reporte_pdf.html')
    html = template.render({
        'ingresos': ingresos,
        'mostrar_costos': mostrar_costos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'tipo_reporte': tipo_reporte,
        'total_ingresos': total_ingresos,
        'total_nomina': total_nomina,
        'total_factura': total_factura,
        'usuario': request.user.username,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF')

    return response


@login_required
def importar_csv(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']

        if not archivo.name.endswith('.csv'):
            messages.error(request, 'El archivo debe ser CSV.')
            return redirect('importar_csv')

        archivo_decodificado = archivo.read().decode('utf-8')
        lector = csv.DictReader(io.StringIO(archivo_decodificado))

        registros_guardados = 0
        errores = []

        for fila_num, fila in enumerate(lector, start=2):
            try:
                empresa_nombre = fila['empresa'].strip()
                empleado_nombre = fila['empleado'].strip()

                empresa = Empresa.objects.get(nombre=empresa_nombre)
                empleado = Empleado.objects.get(nombre=empleado_nombre)

                fecha_entrevista = datetime.strptime(
                    fila['fecha_entrevista'].strip(), '%Y-%m-%d'
                ).date()
                fecha_ingreso = datetime.strptime(
                    fila['fecha_ingreso'].strip(), '%Y-%m-%d'
                ).date()

                Ingreso.objects.create(
                    empresa=empresa,
                    empleado=empleado,
                    capturado_por=request.user,
                    puesto=fila['puesto'].strip(),
                    nombre_completo=fila['nombre_completo'].strip(),
                    curp=fila['curp'].strip(),
                    telefono=fila['telefono'].strip(),
                    fecha_entrevista=fecha_entrevista,
                    fecha_ingreso=fecha_ingreso,
                    monto_estimado=fila['monto_estimado'].strip(),
                )

                registros_guardados += 1

            except Empresa.DoesNotExist:
                errores.append(f'Fila {fila_num}: la empresa "{fila.get("empresa", "")}" no existe.')
            except Empleado.DoesNotExist:
                errores.append(f'Fila {fila_num}: el empleado "{fila.get("empleado", "")}" no existe.')
            except Exception as e:
                errores.append(f'Fila {fila_num}: {str(e)}')

        if registros_guardados > 0:
            messages.success(request, f'Se importaron {registros_guardados} registros correctamente.')

        for error in errores:
            messages.error(request, error)

        return redirect('importar_csv')

    return render(request, 'core/importar_csv.html')