from rest_framework import serializers

from .models import CuentaBancaria


class CuentaBancariaSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = CuentaBancaria

        fields = '__all__'

        read_only_fields = [
            'id',
            'usuario',
            'numero_cuenta',
            'fecha_apertura',
        ]


    def validate(self, datos):

        tipo_cuenta = datos.get(
            'tipo_cuenta',
            getattr(
                self.instance,
                'tipo_cuenta',
                None
            )
        )

        sueldo_mensual = datos.get(
            'sueldo_mensual',
            getattr(
                self.instance,
                'sueldo_mensual',
                0
            )
        )


        if (
            tipo_cuenta == 'CORRIENTE'
            and sueldo_mensual < 600000
        ):

            raise serializers.ValidationError({
                'sueldo_mensual':
                    'Para abrir una Cuenta Corriente '
                    'se requiere una renta mensual '
                    'mínima de $600.000.'
            })

        if sueldo_mensual and sueldo_mensual > 50000000:
            raise serializers.ValidationError({
                'sueldo_mensual':
                    'La renta mensual no puede superar los $50.000.000 CLP.'
            })

        titular = datos.get(
            'titular',
            getattr(self.instance, 'titular', '')
        )

        if titular:
            partes = titular.strip().split()
            if len(partes) < 2:
                raise serializers.ValidationError({
                    'titular':
                        'Debe ingresar al menos un nombre y un apellido.'
                })

        return datos