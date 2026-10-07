from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.inicio,
        name='inicio'
    ),

    path(
        'cuentas/',
        views.listar_cuentas,
        name='listar_cuentas'
    ),

    path(
        'abre-tu-cuenta/',
        views.crear_cuenta,
        name='crear_cuenta'
    ),

    path(
        'cuenta/<int:cuenta_id>/',
        views.detalle_cuenta,
        name='detalle_cuenta'
    ),

    path(
        'cuenta/<int:cuenta_id>/editar/',
        views.editar_cuenta,
        name='editar_cuenta'
    ),

    path(
        'cuenta/<int:cuenta_id>/eliminar/',
        views.eliminar_cuenta,
        name='eliminar_cuenta'
    ),

    path(
        'cuenta/<int:cuenta_id>/solicitar-tarjeta/',
        views.solicitar_tarjeta_credito,
        name='solicitar_tarjeta_credito'
    ),
    
    path(
    'cuenta/<int:cuenta_id>/solicitar-cuenta-corriente/',
    views.solicitar_cuenta_corriente,
    name='solicitar_cuenta_corriente'
),
]