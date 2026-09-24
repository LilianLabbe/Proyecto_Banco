from django.shortcuts import render, redirect, get_object_or_404

from .models import CuentaBancaria
from .forms import CrearCuentaForm, EditarCuentaForm


# ---------------------------------------------------------
# INICIO
# ---------------------------------------------------------

def inicio(request):

    total_cuentas = CuentaBancaria.objects.count()

    cuentas_activas = CuentaBancaria.objects.filter(
        estado='ACTIVA'
    ).count()

    cuentas_corrientes = CuentaBancaria.objects.filter(
        tipo_cuenta='CORRIENTE'
    ).count()

    context = {
        'total_cuentas': total_cuentas,
        'cuentas_activas': cuentas_activas,
        'cuentas_corrientes': cuentas_corrientes,
    }

    return render(
        request,
        'cuentas/inicio.html',
        context
    )


# ---------------------------------------------------------
# LISTAR CUENTAS
# READ
# ---------------------------------------------------------

def listar_cuentas(request):

    cuentas = CuentaBancaria.objects.all()

    return render(
        request,
        'cuentas/listar.html',
        {
            'cuentas': cuentas
        }
    )


# ---------------------------------------------------------
# ABRIR CUENTA
# CREATE
# ---------------------------------------------------------

def crear_cuenta(request):

    if request.method == 'POST':

        formulario = CrearCuentaForm(
            request.POST
        )

        if formulario.is_valid():

            cuenta = formulario.save()

            return redirect(
                'detalle_cuenta',
                cuenta_id=cuenta.id
            )

    else:

        formulario = CrearCuentaForm()

    return render(
        request,
        'cuentas/crear.html',
        {
            'formulario': formulario
        }
    )


# ---------------------------------------------------------
# DETALLE / PORTAL DEL CLIENTE
# ---------------------------------------------------------

def detalle_cuenta(request, cuenta_id):

    cuenta = get_object_or_404(
        CuentaBancaria,
        id=cuenta_id
    )

    return render(
        request,
        'cuentas/detalle.html',
        {
            'cuenta': cuenta
        }
    )


# ---------------------------------------------------------
# EDITAR CUENTA
# UPDATE
# ---------------------------------------------------------

def editar_cuenta(request, cuenta_id):

    cuenta = get_object_or_404(
        CuentaBancaria,
        id=cuenta_id
    )

    if request.method == 'POST':

        formulario = EditarCuentaForm(
            request.POST,
            instance=cuenta
        )

        if formulario.is_valid():

            formulario.save()

            return redirect(
                'detalle_cuenta',
                cuenta_id=cuenta.id
            )

    else:

        formulario = EditarCuentaForm(
            instance=cuenta
        )

    return render(
        request,
        'cuentas/editar.html',
        {
            'formulario': formulario,
            'cuenta': cuenta
        }
    )


# ---------------------------------------------------------
# ELIMINAR CUENTA
# DELETE
# ---------------------------------------------------------

def eliminar_cuenta(request, cuenta_id):

    cuenta = get_object_or_404(
        CuentaBancaria,
        id=cuenta_id
    )

    if request.method == 'POST':

        cuenta.delete()

        return redirect(
            'listar_cuentas'
        )

    return render(
        request,
        'cuentas/eliminar.html',
        {
            'cuenta': cuenta
        }
    )

def solicitar_tarjeta_credito(request, cuenta_id):

    cuenta = get_object_or_404(
        CuentaBancaria,
        id=cuenta_id
    )

    if request.method == "POST":

        if (
            cuenta.puede_tarjeta_credito
            and not cuenta.tarjeta_credito_solicitada
        ):

            cuenta.tarjeta_credito_solicitada = True
            cuenta.save()

    return redirect(
        'detalle_cuenta',
        cuenta_id=cuenta.id
    )