from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
)

from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from .models import CuentaBancaria

from .forms import (
    CrearCuentaForm,
    EditarCuentaForm,
    RegistroClienteForm,
)


# ---------------------------------------------------------
# INICIO
# ---------------------------------------------------------

@login_required
def inicio(request):

    # ADMIN / SUPERUSUARIO
    # Puede ver estadísticas generales

    if request.user.is_superuser:

        total_cuentas = (
            CuentaBancaria.objects.count()
        )

        cuentas_activas = (
            CuentaBancaria.objects
            .filter(
                estado='ACTIVA'
            )
            .count()
        )

        cuentas_corrientes = (
            CuentaBancaria.objects
            .filter(
                tipo_cuenta='CORRIENTE'
            )
            .count()
        )

        context = {
            'total_cuentas': total_cuentas,
            'cuentas_activas': cuentas_activas,
            'cuentas_corrientes': cuentas_corrientes,
            'es_admin': True,
        }

        return render(
            request,
            'cuentas/inicio.html',
            context
        )


    # CLIENTE NORMAL
    # Solo ve su propia cuenta

    try:

        cuenta = request.user.cuenta_bancaria

    except CuentaBancaria.DoesNotExist:

        return render(
            request,
            'cuentas/inicio.html',
            {
                'sin_cuenta': True,
                'es_admin': False,
            }
        )


    return redirect(
        'detalle_cuenta',
        cuenta_id=cuenta.id
    )


# ---------------------------------------------------------
# LISTAR CUENTAS
# ---------------------------------------------------------

@login_required
def listar_cuentas(request):

    # Solo el administrador puede listar todas las cuentas

    if request.user.is_superuser:

        cuentas = (
            CuentaBancaria.objects.all()
        )

    else:

        cuentas = (
            CuentaBancaria.objects
            .filter(
                usuario=request.user
            )
        )


    return render(
        request,
        'cuentas/listar.html',
        {
            'cuentas': cuentas
        }
    )


# ---------------------------------------------------------
# ABRIR CUENTA
# ---------------------------------------------------------

@login_required
def crear_cuenta(request):

    # Un cliente normal solo puede tener una cuenta

    if (
        not request.user.is_superuser
        and CuentaBancaria.objects.filter(
            usuario=request.user
        ).exists()
    ):

        cuenta = CuentaBancaria.objects.get(
            usuario=request.user
        )

        return redirect(
            'detalle_cuenta',
            cuenta_id=cuenta.id
        )


    if request.method == 'POST':

        formulario = CrearCuentaForm(
            request.POST
        )

        if formulario.is_valid():

            cuenta = formulario.save(
                commit=False
            )


            # Si es cliente normal,
            # la cuenta queda asociada a él

            if not request.user.is_superuser:

                cuenta.usuario = (
                    request.user
                )


            cuenta.save()


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

@login_required
def detalle_cuenta(
    request,
    cuenta_id
):

    # ADMIN
    # Puede consultar cualquier cuenta

    if request.user.is_superuser:

        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id
        )

    else:

        # CLIENTE
        # Solo puede consultar su propia cuenta

        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id,
            usuario=request.user
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
# ---------------------------------------------------------

@login_required
def editar_cuenta(
    request,
    cuenta_id
):

    # ADMIN

    if request.user.is_superuser:

        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id
        )

    else:

        # CLIENTE
        # Solo puede editar su propia cuenta

        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id,
            usuario=request.user
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
# ---------------------------------------------------------

@login_required
def eliminar_cuenta(
    request,
    cuenta_id
):

    # Por seguridad dejamos eliminar solamente al admin

    if not request.user.is_superuser:

        return redirect('inicio')


    cuenta = get_object_or_404(
        CuentaBancaria,
        id=cuenta_id
    )


    if request.method == 'POST':

        usuario = cuenta.usuario

        cuenta.delete()


        # Si la cuenta tenía usuario asociado,
        # también eliminamos ese usuario
        # solamente en esta operación administrativa

        if usuario:

            usuario.delete()


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


# ---------------------------------------------------------
# SOLICITAR TARJETA DE CRÉDITO
# ---------------------------------------------------------

@login_required
def solicitar_tarjeta_credito(
    request,
    cuenta_id
):

    # ADMIN

    if request.user.is_superuser:

        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id
        )

    else:

        # CLIENTE
        # Solo puede solicitar para su cuenta

        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id,
            usuario=request.user
        )


    if request.method == "POST":

        if (
            cuenta.puede_tarjeta_credito
            and not
            cuenta.tarjeta_credito_solicitada
        ):

            cuenta.tarjeta_credito_solicitada = True

            cuenta.save()


    return redirect(
        'detalle_cuenta',
        cuenta_id=cuenta.id
    )

# ---------------------------------------------------------
# SOLICITAR CUENTA CORRIENTE 
# ---------------------------------------------------------
@login_required
def solicitar_cuenta_corriente(request, cuenta_id):

    if request.method != 'POST':
        return redirect('detalle_cuenta', cuenta_id=cuenta_id)

    # ADMIN: puede trabajar con cualquier cuenta
    if request.user.is_superuser:
        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id
        )

    # CLIENTE: solo puede modificar su propia cuenta
    else:
        cuenta = get_object_or_404(
            CuentaBancaria,
            id=cuenta_id,
            usuario=request.user
        )

    # Si ya tiene cuenta corriente, no hacemos nada
    if cuenta.tipo_cuenta == 'CORRIENTE':
        return redirect(
            'detalle_cuenta',
            cuenta_id=cuenta.id
        )

    # Validar renta mínima
    if not cuenta.puede_cuenta_corriente:
        return redirect(
            'detalle_cuenta',
            cuenta_id=cuenta.id
        )

    # Cambiar producto de Débito a Corriente
    cuenta.tipo_cuenta = 'CORRIENTE'
    cuenta.save()

    return redirect(
        'detalle_cuenta',
        cuenta_id=cuenta.id
    )

# ---------------------------------------------------------
# REGISTRO DE CLIENTE
# ---------------------------------------------------------

def registrar_cliente(request):

    # Si ya inició sesión,
    # no necesita volver a registrarse

    if request.user.is_authenticated:

        return redirect(
            'inicio'
        )


    if request.method == 'POST':

        formulario = RegistroClienteForm(
            request.POST
        )


        if formulario.is_valid():

            rut = (
                formulario.cleaned_data[
                    'rut'
                ]
            )

            correo = (
                formulario.cleaned_data[
                    'correo'
                ]
            )

            password = (
                formulario.cleaned_data[
                    'password1'
                ]
            )


            # -----------------------------------------
            # CREAR USUARIO DJANGO
            # username = RUT
            # -----------------------------------------

            usuario = User.objects.create_user(
                username=rut,
                email=correo,
                password=password
            )


            # -----------------------------------------
            # CREAR CUENTA BANCARIA
            # -----------------------------------------

            cuenta = (
                CuentaBancaria.objects.create(
                    usuario=usuario,

                    titular=(
                        formulario.cleaned_data[
                            'titular'
                        ]
                    ),

                    rut=rut,

                    telefono=(
                        formulario.cleaned_data[
                            'telefono'
                        ]
                    ),

                    correo=correo,

                    sueldo_mensual=(
                        formulario.cleaned_data[
                            'sueldo_mensual'
                        ]
                    ),

                    tipo_cuenta=(
                        formulario.cleaned_data[
                            'tipo_cuenta'
                        ]
                    ),

                    estado='ACTIVA',
                )
            )


            # -----------------------------------------
            # INICIAR SESIÓN AUTOMÁTICAMENTE
            # -----------------------------------------

            auth_login(
                request,
                usuario
            )


            # -----------------------------------------
            # CREAR TOKEN REST
            # -----------------------------------------

            token, creado = (
                Token.objects.get_or_create(
                    user=usuario
                )
            )


            request.session[
                'api_token'
            ] = token.key


            return redirect(
                'detalle_cuenta',
                cuenta_id=cuenta.id
            )

    else:

        formulario = RegistroClienteForm()


    return render(
        request,
        'registration/registro.html',
        {
            'formulario': formulario
        }
    )


# ---------------------------------------------------------
# LOGIN PERSONALIZADO
# CLIENTES CON RUT + ADMIN CON USERNAME
# ---------------------------------------------------------

def login_personalizado(request):

    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':

        identificador = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        # Primero intentamos interpretar
        # el identificador como RUT.

        username = identificador

        try:
            from .models import normalizar_rut

            username = normalizar_rut(
                identificador
            )

        except Exception:
            # Si no es RUT, dejamos el valor tal cual.
            # Esto permite que el administrador
            # siga entrando como "Lilian".
            username = identificador

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:

            auth_login(
                request,
                usuario
            )

            token, creado = Token.objects.get_or_create(
                user=usuario
            )

            request.session[
                'api_token'
            ] = token.key

            return redirect(
                'inicio'
            )

        return render(
            request,
            'registration/login.html',
            {
                'error':
                    'RUT/usuario o contraseña incorrectos.'
            }
        )

    return render(
        request,
        'registration/login.html'
    )

# ---------------------------------------------------------
# CERRAR SESIÓN
# ---------------------------------------------------------

@login_required
def cerrar_sesion(request):

    if request.method == 'POST':

        # Elimina el token REST

        Token.objects.filter(
            user=request.user
        ).delete()


        # Elimina el token guardado
        # dentro de la sesión Django

        request.session.pop(
            'api_token',
            None
        )


        # Cierra la sesión web

        auth_logout(
            request
        )


        return redirect(
            'login'
        )


    return redirect(
        'inicio'
    )