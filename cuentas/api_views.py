from django.contrib.auth import authenticate

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import CuentaBancaria
from .serializers import CuentaBancariaSerializer


# ---------------------------------------------------------
# LOGIN API
# ---------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:

        return Response(
            {
                'error':
                    'Debe ingresar RUT/usuario y contraseña.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    usuario = authenticate(
        username=username,
        password=password
    )

    if usuario is None:

        return Response(
            {
                'error':
                    'RUT/usuario o contraseña incorrectos.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, creado = Token.objects.get_or_create(
        user=usuario
    )

    return Response(
        {
            'mensaje':
                'Inicio de sesión correcto.',
            'usuario':
                usuario.username,
            'token':
                token.key
        },
        status=status.HTTP_200_OK
    )


# ---------------------------------------------------------
# LOGOUT API
# ---------------------------------------------------------

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_logout(request):

    if request.auth:

        request.auth.delete()

    return Response(
        {
            'mensaje':
                'Sesión cerrada correctamente.'
        },
        status=status.HTTP_200_OK
    )


# ---------------------------------------------------------
# CRUD API CUENTAS
# ---------------------------------------------------------

class CuentaBancariaViewSet(
    viewsets.ModelViewSet
):

    serializer_class = (
        CuentaBancariaSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


    # -----------------------------------------------------
    # QUÉ CUENTAS PUEDE VER CADA USUARIO
    # -----------------------------------------------------

    def get_queryset(self):

        usuario = self.request.user

        # ADMIN
        # Puede ver todas las cuentas

        if usuario.is_superuser:

            return (
                CuentaBancaria.objects.all()
            )

        # CLIENTE
        # Solo puede ver su propia cuenta

        return (
            CuentaBancaria.objects.filter(
                usuario=usuario
            )
        )


    # -----------------------------------------------------
    # CREAR CUENTA
    # -----------------------------------------------------

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        usuario = request.user

        # ADMIN
        # Puede crear cuentas manualmente

        if usuario.is_superuser:

            return super().create(
                request,
                *args,
                **kwargs
            )

        # CLIENTE
        # Si ya tiene cuenta, no puede crear otra

        if CuentaBancaria.objects.filter(
            usuario=usuario
        ).exists():

            return Response(
                {
                    'error':
                        'Este usuario ya tiene '
                        'una cuenta bancaria.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            usuario=usuario
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


    # -----------------------------------------------------
    # ACTUALIZAR CUENTA COMPLETA
    # -----------------------------------------------------

    def update(
        self,
        request,
        *args,
        **kwargs
    ):

        cuenta = self.get_object()

        # ADMIN
        # Puede usar el serializer completo

        if request.user.is_superuser:

            return super().update(
                request,
                *args,
                **kwargs
            )

        # CLIENTE NORMAL
        # Solo permitimos determinados campos

        campos_permitidos = [
            'telefono',
            'correo',
        ]

        datos = {}

        for campo in campos_permitidos:

            if campo in request.data:

                datos[campo] = (
                    request.data[campo]
                )

        serializer = self.get_serializer(
            cuenta,
            data=datos,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )


    # -----------------------------------------------------
    # PATCH / ACTUALIZACIÓN PARCIAL
    # -----------------------------------------------------

    def partial_update(
        self,
        request,
        *args,
        **kwargs
    ):

        return self.update(
            request,
            *args,
            **kwargs
        )


    # -----------------------------------------------------
    # ELIMINAR CUENTA
    # -----------------------------------------------------

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):

        # Solo el administrador
        # puede eliminar cuentas

        if not request.user.is_superuser:

            return Response(
                {
                    'error':
                        'No tiene permisos '
                        'para eliminar esta cuenta.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )