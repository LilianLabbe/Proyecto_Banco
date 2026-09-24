from django.contrib import admin
from .models import CuentaBancaria


@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):

    list_display = (
        'numero_cuenta',
        'titular',
        'rut',
        'tipo_cuenta',
        'sueldo_mensual',
        'saldo',
        'estado',
        'fecha_apertura',
    )

    search_fields = (
        'numero_cuenta',
        'titular',
        'rut',
        'correo',
    )

    list_filter = (
        'tipo_cuenta',
        'estado',
        'fecha_apertura',
    )

    readonly_fields = (
        'numero_cuenta',
        'fecha_apertura',
    )