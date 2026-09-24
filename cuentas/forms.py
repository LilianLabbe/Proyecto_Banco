from django import forms
from .models import CuentaBancaria


class CrearCuentaForm(forms.ModelForm):

    class Meta:

        model = CuentaBancaria

        fields = [
            'titular',
            'rut',
            'telefono',
            'correo',
            'sueldo_mensual',
            'tipo_cuenta',
        ]

        widgets = {

            'titular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'maxlength': '100',
                'autocomplete': 'name'
            }),

            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-5',
                'maxlength': '12'
            }),

            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '912345678',
                'maxlength': '9',
                'inputmode': 'numeric',
                'autocomplete': 'tel'
            }),

            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.cl',
                'maxlength': '150',
                'autocomplete': 'email'
            }),

            'sueldo_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '999999999999',
                'step': '1',
                'placeholder': 'Ej: 750000'
            }),

            'tipo_cuenta': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

        help_texts = {

            'rut': (
                'Se validará el dígito verificador y '
                'el RUT no puede estar registrado anteriormente.'
            ),

            'telefono': (
                'Ingrese un celular chileno de 9 dígitos. '
                'Ejemplo: 912345678.'
            ),

            'sueldo_mensual': (
                'Cuenta Débito: sin renta mínima. '
                'Cuenta Corriente: mínimo $600.000. '
                'Línea de Crédito: disponible desde $900.000.'
            ),

            'tipo_cuenta': (
                'Selecciona el producto que deseas solicitar.'
            ),
        }


class EditarCuentaForm(forms.ModelForm):

    class Meta:

        model = CuentaBancaria

        fields = [
            'titular',
            'rut',
            'telefono',
            'correo',
            'sueldo_mensual',
            'tipo_cuenta',
            'saldo',
            'estado',
        ]

        widgets = {

            'titular': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),

            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '12'
            }),

            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '9',
                'inputmode': 'numeric'
            }),

            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'maxlength': '150'
            }),

            'sueldo_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '999999999999',
                'step': '1'
            }),

            'tipo_cuenta': forms.Select(attrs={
                'class': 'form-select'
            }),

            'saldo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),

            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

        help_texts = {

            'rut': (
                'Debe corresponder a un RUT chileno válido '
                'y no puede pertenecer a otra cuenta.'
            ),

            'telefono': (
                'Celular chileno de 9 dígitos.'
            ),

            'sueldo_mensual': (
                'Cuenta Corriente: mínimo $600.000. '
                'Línea de Crédito: mínimo $900.000.'
            ),
        }